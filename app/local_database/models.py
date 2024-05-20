import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
import passlib.hash as _hash
import app.local_database.database as _database

_database.Base.metadata.create_all(_database.engine)

class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String)
    email = _sql.Column(_sql.String, unique=True, index=True)
    is_verified = _sql.Column(_sql.Boolean , default=False)
    otp = _sql.Column(_sql.Integer)
    hashed_password = _sql.Column(_sql.String)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    products = _orm.relationship("Product", back_populates="owner")


    def verify_password(self, password: str):
        return _hash.bcrypt.verify(password, self.hashed_password)


class Product(_database.Base):
    __tablename__ = "products"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, index=True)
    image_url = _sql.Column(_sql.String, index=True)
    ean = _sql.Column(_sql.String,index=True )
    brand = _sql.Column(_sql.String, index=True)
    category = _sql.Column(_sql.String, index=True)
    price  = _sql.Column(_sql.Integer,index=True)
    description = _sql.Column(_sql.String, index=True)
    owner_id = _sql.Column(_sql.Integer, _sql.ForeignKey("users.id"))

    owner = _orm.relationship("User", back_populates="products")


class Retailproduct(_database.Base):
    __tablename__ = "retailproducts"

    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    name = _sql.Column(_sql.String, index=True)
    image_url = _sql.Column(_sql.String, index=True)
    ean = _sql.Column(_sql.String,index=True)
    brand = _sql.Column(_sql.String, index=True)
    category = _sql.Column(_sql.String, index=True)
    price  = _sql.Column(_sql.Integer,index=True)
    description = _sql.Column(_sql.String, index=True)
   
   