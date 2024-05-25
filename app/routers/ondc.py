from typing import List
from jinja2 import Template  
from fastapi import APIRouter ,HTTPException , Depends , UploadFile ,File 
import fastapi as _fastapi
from fastapi.responses import JSONResponse , HTMLResponse , FileResponse
import sqlalchemy.orm as _orm
import app.local_database.models as _models
import app.local_database.database as _database
import app.auth.auth_services as _services
import app.local_database.schemas as _schemas
from app.ondc.ean_search import scrape_upc
from app.ondc.genai import process_user_input , generate_product_info
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import uuid


from sqlalchemy import func
import app.ondc.rpc_client as rpc_client
from app.logger import Logger
import base64
import os
from dotenv import load_dotenv

load_dotenv()
# Create an instance of the Logger class
logger_instance = Logger()

# Get a logger for your module
logger = logger_instance.get_logger("ondc api")
router = APIRouter(
    tags=["ondc"],)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR,'user_files_upload')

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
    unique_brand_count = db.query(func.count(_models.Product.brand.distinct())).filter_by(owner_id=user.id).scalar()
    logger.info(f"Total count of products retrieved for user_id: {user.id}")
    logger.info(f"Unique category count retrieved for user_id: {user.id}")
    logger.info(f"Unique brand count retrieved for user_id: {user.id}")

    data = {
        "product_total_count": total_count,
        "product_category_count":unique_category_count,
        "total_brands": unique_brand_count
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

        product_details = {
                    'id': "10",
                    "name": "Haldiram aloo bhujia 150 gm",
                    'image_url': "https://www.bigbasket.com/media/uploads/p/xxl/70000800_3-haldirams-namkeen-aloo-bhujia-del.jpg",
                    'ean':"8904063214393",
                    'brand':"Haldiram",
                    'category': "Snacks",
                    'price':"103",
                    'description':"snacks"
                    }

        # ocr_rpc = rpc_client.OcrRpcClient()

        # with open(image.filename, "rb") as buffer:
        #     file_data = buffer.read()
        #     file_base64 = base64.b64encode(file_data).decode()
        
        # request_json = {
        #     'file': file_base64
        #     }

        # # Call the OCR microservice with the request JSON
        # ocrresponse = ocr_rpc.call(request_json)
        # # Delete the temporary image file
        # os.remove(image.filename)

        # embed_rpc = rpc_client.EmbeddingRpcClient()

        # request_json = {
        #     'text': ocrresponse
        #     }

        # # Call the OCR microservice with the request JSON
        # response = embed_rpc.call(request_json)

        # print(response['embeddings'][0])


        
        return product_details

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
        #add logic to handle  if it does not find any key then return None for all keys
        for  items in product_info_list:
            data = {
                "id": str(uuid.uuid4()) ,
                'name': items['name'] if 'name' in items else None,
                'image_url': items['image_url'] if 'image_url' in items else None,
                'ean': items['ASIN_Number'] if 'ASIN_Number' in items else None,
                'brand': items['brand'] if 'brand' in items else None,
                'category': items['category'] if 'category' in items else None,
                'description': items['description'] if 'description' in items else None,
                'price': items['price'] if 'price' in items else None
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


@router.post("/bulk_products_add")
async def bulk_add_products(
    request_data: _schemas.BulkProductRequest,
    user: _schemas.User = Depends(_services.get_current_user),
    db: _orm.Session = Depends(_services.get_db)
):
    added_products = []
    errors = []

    for new_product in request_data.product_details:
        # Check if a product with the same EAN already exists
        existing_product = db.query(_models.Product).filter(_models.Product.ean == new_product.ean, _models.Product.owner_id == user.id).first()

        if existing_product:
            # If a product with the same EAN already exists, add an error message
            errors.append({
                "product": new_product,
                "message": "Product with the same EAN already exists"
            })
        else:
            # Create a new product instance with the provided data
            product_data = new_product.dict()
            product_data["owner_id"] = user.id  # Set the owner_id to the current user's id

            new_product_instance = _models.Product(**product_data)
            logger.info(f"New product added for user_id: {user.id}")

            db.add(new_product_instance)
            db.commit()
            db.refresh(new_product_instance)
            
            added_products.append(new_product_instance)

    response = {
        "status": "Products processed",
        "added_products": added_products,
        "errors": errors
    }
    return response



@router.get("/share_catalog")
async def share_catalog(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):  
    host =  os.environ.get("HOST_URL")
    base_url = router.url_path_for("render_catalog", user_id=user.id)
    response  = {
        "public_url": host+base_url
    }
    return response
    

@router.get("/viewcatalog/{user_id}")
async def render_catalog(user_id: str ,
                         db: _orm.Session = _fastapi.Depends(_services.get_db)):

    all_products = db.query(_models.Product).filter_by(owner_id=user_id).all()
    logger.info(f"All products retrived for user_id:  {user_id}")

    if not all_products:
        return HTMLResponse(content="Catalog not found", status_code=404)
    
    template_dir = "app/templates"  # Replace with your actual template directory
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("catalogue.html") 

    rendered_template = template.render(catalog_items=all_products)
    return HTMLResponse(content=rendered_template, media_type="text/html")




@router.get("/get_catalog/", response_class=FileResponse )
async def download_catalog(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    
     # Query all products for the current user
    all_products = db.query(_models.Product).filter_by(owner_id=user.id).all()

    # Convert the queried data into a DataFrame
    product_data = [{"id": product.id, "name": product.name, "brand":product.brand, "ean":product.ean, "category":product.category, "price":product.price, "image_url":product.image_url, "description": product.description,  } for product in all_products]
    df = pd.DataFrame(product_data)

    # Define the file path to save the CSV
    file_path = BASE_DIR + "/get_catalog_file/products.csv"

    # Save the DataFrame to a CSV file
    df.to_csv(file_path, index=False)
    file_path = file_path
    response = FileResponse(file_path, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=downloaded_file.csv"
    return response




# @app.post("/upload_catalog/")
# async def upload_catalog(
#     file: UploadFile = File(...),
#     user: _schemas.User = _fastapi.Depends(_services.get_current_user),
#     db: _orm.Session = _fastapi.Depends(_services.get_db)
# ):

#     # Validate the uploaded file
#     if not file.content_type.startswith("text/csv"):
#         raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

#     # Read the uploaded CSV data into a DataFrame
#     try:
#         df = pd.read_csv(file.file)
#     except pd.errors.ParserError as e:
#         raise HTTPException(status_code=400, detail=f"Error parsing CSV file: {str(e)}")

#     # Validate DataFrame columns
#     expected_columns = {"name", "brand", "ean", "category", "price", "image_url", "description"}
#     if not all(col in df.columns for col in expected_columns):
#         raise HTTPException(status_code=400, detail = 
