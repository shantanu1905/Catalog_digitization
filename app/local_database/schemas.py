import datetime
import pydantic 
from typing import List, Optional


class UserBase(pydantic.BaseModel):
    name: str
    email: str
    class Config:
       from_attributes=True

class UserCreate(UserBase):
    password: str
    class Config:
       from_attributes=True

class User(UserBase):
    id: int
    date_created: datetime.datetime
    class Config:
       from_attributes=True


class GenerateUserToken(pydantic.BaseModel):
    username: str
    password: str
    class Config:
        orm_mode = True
        from_attributes=True

class GenerateOtp(pydantic.BaseModel):
    email: str
    
class VerifyOtp(pydantic.BaseModel):
    email: str
    otp: int



class Product(pydantic.BaseModel):
    name: str
    image_url : str
    ean : str
    brand: str
    category:str
    price:str
    description: str = None

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line to enable from_orm


class EAN(pydantic.BaseModel):
    ean : int

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line to enable from_orm
   

class VoiceSearch(pydantic.BaseModel):
    voice_input : str

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line to enable from_orm
   
class BulkProductRequest(pydantic.BaseModel):
    product_details: List[Product]

    class Config:
        orm_mode = True