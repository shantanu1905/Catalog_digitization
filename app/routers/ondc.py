from typing import List
from fastapi import APIRouter , FastAPI ,HTTPException , Depends
import fastapi as _fastapi
from fastapi.responses import JSONResponse 
import sqlalchemy.orm as _orm
import app.local_database.models as _models
import app.local_database.database as _database
import app.auth.auth_services as _services
import app.local_database.schemas as _schemas
from app.ondc.ean_search import scrape_upc
from fastapi.templating import Jinja2Templates
from app.logger import Logger



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

    data = {
        "products" :all_products}

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

    db.add(new_product_instance)
    db.commit()
    db.refresh(new_product_instance)

    data = {
        "status": "Product Details Added Successfully",
        "product_details": new_product_instance
    }
    return data

