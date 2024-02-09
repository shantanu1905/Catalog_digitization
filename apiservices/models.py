import datetime as _dt

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
from apiservices.database import Base , engine
from apiservices import database as _database


Base.metadata.create_all(engine)
class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    email = _sql.Column(_sql.String, unique=True, index=True)
    hashed_password = _sql.Column(_sql.String)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

    posts = _orm.relationship("Post", back_populates="owner")
    products = _orm.relationship("Product", back_populates="owner")

    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)

class Post(_database.Base):
    __tablename__ = "posts"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"))
    post_text = _sql.Column(_sql.String, index=True)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)

    owner = _orm.relationship("User", back_populates="posts")


class Product(_database.Base):
    __tablename__ = "products"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, index=True)
    image_url = _sql.Column(_sql.String, index=True)
    ean = _sql.Column(_sql.Integer,index=True)
    brand = _sql.Column(_sql.String, index=True)
    category = _sql.Column(_sql.String, index=True)
    price  = _sql.Column(_sql.Integer,index=True)
    description = _sql.Column(_sql.String, index=True)
    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"))

    owner = _orm.relationship("User", back_populates="products")