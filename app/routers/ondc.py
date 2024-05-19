from typing import List
from fastapi import APIRouter ,HTTPException , Depends , UploadFile ,File
import fastapi as _fastapi
from fastapi.responses import JSONResponse 
import sqlalchemy.orm as _orm
import app.local_database.models as _models
import app.local_database.database as _database
import app.auth.auth_services as _services
import app.local_database.schemas as _schemas
from app.ondc.ean_search import scrape_upc
from app.ondc.genai import process_user_input , generate_product_info


from sqlalchemy import func
import app.ondc.rpc_client as rpc_client
from app.logger import Logger
import base64
import os



# Create an instance of the Logger class
logger_instance = Logger()

# Get a logger for your module
logger = logger_instance.get_logger("ondc api")
router = APIRouter(
    tags=["ondc"],)



@router.post("/search_ean" )
async def search_ean(
    upc_number: _schemas.EAN,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_database.get_db)
):  
    
    dbresponse = db.query(_models.Retailproduct).filter(_models.Retailproduct.ean == str(upc_number.ean)).first()
    if dbresponse is not None:
        response = {
            'name' : dbresponse.name,
            'image_url' : dbresponse.image_url,
            'ean' : dbresponse.ean,
            'brand' : dbresponse.brand,
            'category' : dbresponse.category
        }
    else:
        if dbresponse is None:
            logger.info(f"EAN for product Not found in database: {upc_number.ean}")
            response = await scrape_upc(upc_number.ean)
            logger.info(f"Going for EAN API for product search:  {upc_number.ean}")

            if response is None:
                return JSONResponse(content={"message": "Sorry, we were not able to find a product"}, status_code=404)
    try:
        # print(f"Search EAN Response: {response}")
        return JSONResponse(content=response, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"message": "Sorry, we were not able to find a product"}, status_code=404)





# Get all products for the current user
@router.get("/get_products" , )
async def get_all_products(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    all_products = db.query(_models.Product).filter_by(owner_id=user.id).all()
    logger.info(f"All products retrived for user_id:  {user.id}")

    data = {
        "products" :all_products}

    return data



@router.get("/products_stats")
async def get_products_stats(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    total_count = db.query(func.count(_models.Product.id)).filter_by(owner_id=user.id).scalar()
    unique_category_count = db.query(func.count(_models.Product.category.distinct())).filter_by(owner_id=user.id).scalar()
    logger.info(f"Total count of products retrieved for user_id: {user.id}")
    logger.info(f"Unique category count retrieved for user_id: {user.id}")

    data = {
        "product_total_count": total_count,
        "product_category_count":unique_category_count
    }

    return data



# Get a product by id
@router.get("/products/{product_id}" , )
async def get_product(
    product_id: int,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    existing_product = db.query(_models.Product).filter_by(id=product_id, owner_id=user.id).first()

    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return existing_product

# update a  product by id
@router.put("/product_update/{product_id}" ,  )
async def update_product(
    product_id: int,
    updated_product: _schemas.Product,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    existing_product = db.query(_models.Product).filter_by(id=product_id, owner_id=user.id).first()

    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update fields with non-None values from the request
    for field, value in updated_product.dict(exclude_unset=True).items():
        setattr(existing_product, field, value)

    db.commit()
    db.refresh(existing_product)

    data = {
        "status" : "Product Details Updated Successfully",
        "product_details" : existing_product
    }

    return data

# Delete an existing product by id
@router.delete("/products/{product_id}" , )
async def delete_product(
    product_id: int,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    existing_product = db.query(_models.Product).filter_by(id=product_id, owner_id=user.id).first()

    if existing_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(existing_product)
    db.commit()

    return {"message": "Product deleted successfully"}

# Add a new product
@router.post("/products_add" , )
async def add_product(
    new_product: _schemas.Product,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    # Check if a product with the same EAN already exists
    existing_product = db.query(_models.Product).filter(_models.Product.ean == new_product.ean , _models.Product.owner_id==user.id).first()

    if existing_product:
        # If a product with the same EAN already exists, return an error message
        return {"status": "Error", "message": "Product with the same EAN already exists"}

    # Create a new product instance with the provided data
    product_data = new_product.dict()
    product_data["owner_id"] = user.id  # Set the owner_id to the current user's id

    new_product_instance = _models.Product(**product_data)
    logger.info(f"New product added for user_id: {user.id}")

    db.add(new_product_instance)
    db.commit()
    db.refresh(new_product_instance)

    data = {
        "status": "Product Details Added Successfully",
        "product_details": new_product_instance
    }
    return data


# ml microservice route - OCR route
@router.post('/ocr' ,  )
def ocr(file: UploadFile = File(...),
        user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    
    # Save the uploaded file to a temporary location
    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())

    ocr_rpc = rpc_client.OcrRpcClient()

    with open(file.filename, "rb") as buffer:
        file_data = buffer.read()
        file_base64 = base64.b64encode(file_data).decode()
    
    request_json = {
        'file': file_base64
        }

    # Call the OCR microservice with the request JSON
    response = ocr_rpc.call(request_json)

    # Delete the temporary image file
    os.remove(file.filename)

    return response


@router.post("/product_search_by_image" )
async def upload_image(
    image: UploadFile = File(...) ,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
    ):
    try:
        # Save the uploaded file to a temporary location
        with open(image.filename, "wb") as buffer:
            buffer.write(image.file.read())

        ocr_rpc = rpc_client.OcrRpcClient()

        with open(image.filename, "rb") as buffer:
            file_data = buffer.read()
            file_base64 = base64.b64encode(file_data).decode()
        
        request_json = {
            'file': file_base64
            }

        # Call the OCR microservice with the request JSON
        response = ocr_rpc.call(request_json)

        



        
        return JSONResponse(content={'status':'success' , 'product_details': search_result}, status_code=200)

    except Exception as e:
        response = {
            'status':'failed',
            'product_details': 'Not found.'
        }
        return JSONResponse(content=response, status_code=404)
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/product_voice_search" )
async def voice_search(
    user_input:  _schemas.VoiceSearch ,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
    ):
    try:
        logger.info(f"voice based products search initiated for user_id:{user.id}")
        product_names = process_user_input(user_input.voice_input)
        product_info_list = generate_product_info(product_names)

        response = []
        #add logic to handle  if it does not find any key then return None
        for items in product_info_list:
            data = {
                'name': items['name'],
               
                'brand': items['brand'],
                'category': items['category'],
                'description': items['description'],
                'price': items['price']
            }
            response.append(data)
        return JSONResponse(content={'status':'success' , 'product_details': response}, status_code=200)

    except Exception as e:
        response = {
            'status':'failed',
            'product_details': 'Try Again, Slow down when you speak, Mention *add* keyword before you take any product name.'
        }
        return JSONResponse(content=response, status_code=404)
        raise HTTPException(status_code=500, detail=str(e))





