import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .logger import Logger

log = Logger()
logger = log.get_logger(__name__)
load_dotenv()
"""Create a connection to the backend default database """
DATABASE_URL = (
    "postgresql://{username}:{password}@{host}:{port}/{database_name}".format(
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database_name=os.getenv("DB_NAME"),
    )
)


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    return db
