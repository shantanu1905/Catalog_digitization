from typing import List
from fastapi import HTTPException 
import fastapi as _fastapi
from fastapi import FastAPI, UploadFile, HTTPException, File
import shutil
import os
import fastapi.security as _security
from fastapi.responses import HTMLResponse , JSONResponse , FileResponse
import sqlalchemy.orm as _orm
import apiservices.models as _models
import apiservices.services as _services
import apiservices.schemas as _schemas
import pandas as pd
from apiservices.helper_services import scrape_upc  , delete_previous_image ,search_by_embedding ,  search_by_embedding_voice
from fastapi import Request
from fastapi.templating import Jinja2Templates



app = _fastapi.FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR,'user_files_upload')



templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Render the "index.html" template
    return templates.TemplateResponse("index.html", {"request": request})




@app.post("/api/users" ,  tags = ['User Auth'])
async def create_user(
    user: _schemas.UserCreate, 
    db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_email(email=user.email, db=db)

    if db_user:
        raise _fastapi.HTTPException(
            status_code=200,
            detail="User with that email already exists")

    user = await _services.create_user(user=user, db=db)

    return await _services.create_token(user=user)



# Endpoint to check if the API is live
@app.get("/check_api")
async def check_api():
    return {"status": "Connected to API Successfully"}



@app.post("/api/token" ,tags = ['User Auth'])
async def generate_token(
    #form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(), 
    user_data: _schemas.GenerateUserToken,
    db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = await _services.authenticate_user(email=user_data.username, password=user_data.password, db=db)

    if not user:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user=user)


@app.get("/api/users/me", response_model=_schemas.User  , tags = ['User Auth'])
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user


# @app.post("/api/user-posts", response_model=_schemas.Post)
# async def create_post(
#     post: _schemas.PostCreate,
#     user: _schemas.User = _fastapi.Depends(_services.get_current_user),
#     db: _orm.Session = _fastapi.Depends(_services.get_db)
# ):
#     return await _services.create_post(user=user, db=db, post=post)


# @app.get("/api/my-posts", response_model=List[_schemas.Post])
# async def get_user_posts(user: _schemas.User = _fastapi.Depends(_services.get_current_user),
#                          db: _orm.Session = _fastapi.Depends(_services.get_db)):
#     return await _services.get_user_posts(user=user, db=db)


@app.post("/search_ean" ,  tags = ['Retail Product'])
async def search_ean(
    upc_number: _schemas.EAN,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    response = await scrape_upc(upc_number.ean)

    if response is None:
        return JSONResponse(content={"message": "Sorry, we were not able to find a product"}, status_code=404)

    try:
        print(f"Search EAN Response: {response}")

        return JSONResponse(content=response, status_code=200)
    except HTTPException as e:
        return JSONResponse(content={"message": "Sorry, we were not able to find a product"}, status_code=404)

# Get all products for the current user
@app.get("/get_products" ,  tags = ['Retail Product'])
async def get_all_products(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    all_products = db.query(_models.Product).filter_by(owner_id=user.id).all()

    data = {
        "products" :all_products}

    return data


# Get a product by id
@app.get("/products/{product_id}" ,  tags = ['Retail Product'])
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
@app.put("/product_update/{product_id}" ,   tags = ['Retail Product'])
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
@app.delete("/products/{product_id}" ,  tags = ['Retail Product'])
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
@app.post("/products_add" ,  tags = ['Retail Product'])
async def add_product(
    new_product: _schemas.Product,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    # Check if a product with the same EAN already exists
    existing_product = db.query(_models.Product).filter(_models.Product.ean == new_product.ean).first()

    if existing_product:
        # If a product with the same EAN already exists, return an error message
        return {"status": "Error", "message": "Product with the same EAN already exists"}

    # Create a new product instance with the provided data
    product_data = new_product.dict()
    product_data["owner_id"] = user.id  # Set the owner_id to the current user's id

    new_product_instance = _models.Product(**product_data)

    db.add(new_product_instance)
    db.commit()
    db.refresh(new_product_instance)

    data = {
        "status": "Product Details Added Successfully",
        "product_details": new_product_instance
    }

    return data


@app.post("/product_search_by_image" , tags = ['Retail Product'])
async def upload_image(
    image: UploadFile = File(...) ,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
    ):
    try:

        # Save the uploaded image to the images folder
        file_path = f"{UPLOAD_DIR}/{image.filename}"
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        search_result = search_by_embedding(file_path)

        # Delete the uploaded audio file
        os.remove(file_path)
        
        return JSONResponse(content={'status':'success' , 'product_details': search_result}, status_code=200)

    except Exception as e:
        response = {
            'status':'failed',
            'product_details': 'Not found.'
        }
        return JSONResponse(content=response, status_code=404)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_catalog/", response_class=FileResponse , tags = ['Retail Product'])
async def download_catalog(
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    
     # Query all products for the current user
    all_products = db.query(_models.Product).filter_by(owner_id=user.id).all()

    # Convert the queried data into a DataFrame
    product_data = [{"id": product.id, "name": product.name, "brand":product.brand, "category":product.category, "price":product.price, "image_url":product.image_url, "description": product.description,  } for product in all_products]
    df = pd.DataFrame(product_data)

    # Define the file path to save the CSV
    file_path = BASE_DIR + "/get_catalog_file/products.csv"

    # Save the DataFrame to a CSV file
    df.to_csv(file_path, index=False)
    file_path = file_path
    response = FileResponse(file_path, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=downloaded_file.csv"
    return response


# FastAPI endpoint for product voice search
@app.post("/product_voice_search" ,  tags = ['Retail Product'])
async def product_voice_search(
    audio: UploadFile = File(...),
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)):
    
    try :
        # Save the uploaded audio file
        audio_file_path = f"{UPLOAD_DIR}/{audio.filename}"
        #print(audio_file_path)
        with open(audio_file_path, "wb") as buffer:
            buffer.write(audio.file.read())

        # Recognize speech from the uploaded audio file
        recognized_text = search_by_embedding_voice(audio_file_path)

        # Delete the uploaded audio file
        os.remove(audio_file_path)

        response = {'status':'success',
                    'product_details': recognized_text}
        return  JSONResponse(content=response, status_code=200)
    
    except Exception as e:
        response = {
            'status':'failed',
            'product_details': 'Not found.'
        }
        os.remove(audio_file_path)
        return JSONResponse(content=response, status_code=404)
        raise HTTPException(status_code=500, detail=str(e))

    