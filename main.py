from typing import List
from fastapi import HTTPException
import fastapi as _fastapi
from fastapi import FastAPI, UploadFile, HTTPException, File, Form
import shutil
import os
import fastapi.security as _security
from fastapi.responses import HTMLResponse , JSONResponse
import sqlalchemy.orm as _orm
import models as _models
import services as _services
import schemas as _schemas
from helper_services import scrape_upc , return_image_embedding , delete_previous_image ,search_by_embedding
app = _fastapi.FastAPI()



@app.post("/api/users" ,  tags = ['User Auth'])
async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
    db_user = await _services.get_user_by_email(email=user.email, db=db)
    if db_user:
        raise _fastapi.HTTPException(
            status_code=400,
            detail="User with that email already exists")

    user = await _services.create_user(user=user, db=db)

    return await _services.create_token(user=user)


@app.post("/api/token" ,tags = ['User Auth'])
async def generate_token(form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(), db: _orm.Session = _fastapi.Depends(_services.get_db)):
    user = await _services.authenticate_user(email=form_data.username, password=form_data.password, db=db)

    if not user:
        raise _fastapi.HTTPException(
            status_code=401, detail="Invalid Credentials")

    return await _services.create_token(user=user)


@app.get("/api/users/me", response_model=_schemas.User  , tags = ['User Auth'])
async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
    return user


@app.post("/api/user-posts", response_model=_schemas.Post)
async def create_post(
    post: _schemas.PostCreate,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    return await _services.create_post(user=user, db=db, post=post)


@app.get("/api/my-posts", response_model=List[_schemas.Post])
async def get_user_posts(user: _schemas.User = _fastapi.Depends(_services.get_current_user),
                         db: _orm.Session = _fastapi.Depends(_services.get_db)):
    return await _services.get_user_posts(user=user, db=db)





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
        print(response)

        # new_product = _models.Product(
        #     name=response['product_name'],
        #     image_url=response['image_source'],
        #     ean=response['ean'],
        #     brand=response['brand'],
        #     category=response['category'],
        #     price=None,
        #     description=None,
        #     owner_id=user.id 
        # )
        # db.add(new_product)
        # db.commit()
        # db.refresh(new_product)

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



# Define the path to the images folder
IMAGES_FOLDER = "images"
# Create the images folder if it doesn't exist
os.makedirs(IMAGES_FOLDER, exist_ok=True)
# Route to handle image upload

@app.post("/product_search_by_image" , tags = ['Retail Product'])
async def upload_image(
    image: UploadFile = File(...) ,
    user: _schemas.User = _fastapi.Depends(_services.get_current_user),
    db: _orm.Session = _fastapi.Depends(_services.get_db)
    ):
    try:
        # Delete previous image, if any
        delete_previous_image()

        # Save the uploaded image to the images folder
        file_path = os.path.join(IMAGES_FOLDER, 'user_image.jpg')
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        img_path='images/user_image.jpg'
        search_result = search_by_embedding(img_path)
        return JSONResponse(content={'status':'success' , 'product_details': search_result}, status_code=200)

    except Exception as e:
        response = {
            'status':'failed',
            'product_details': 'Not found.'
        }
        return JSONResponse(content={response}, status_code=500)
        raise HTTPException(status_code=500, detail=str(e))


