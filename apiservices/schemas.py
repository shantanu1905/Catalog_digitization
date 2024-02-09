import datetime as _dt

import pydantic as _pydantic

class _UserBase(_pydantic.BaseModel):
    email: str

class UserCreate(_UserBase):
    password: str

    class Config:
        orm_mode = True

class User(_UserBase):
    id: int
    date_created: _dt.datetime

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line to enable from_orm

class GenerateUserToken(_pydantic.BaseModel):
    username : str
    password : str


class _PostBase(_pydantic.BaseModel):
    post_text: str

class PostCreate(_PostBase):
    pass

class Post(_PostBase):
    id: int
    owner_id: int
    date_created: _dt.datetime

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line to enable from_orm


class Product(_pydantic.BaseModel):
    name: str
    image_url : str
    ean : str
    brand: str
    category:str
    price:str
    description: str or None = None

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line to enable from_orm


class EAN(_pydantic.BaseModel):
    ean : int

    class Config:
        orm_mode = True
        from_attributes = True  # Add this line to enable from_orm
   