from fastapi import Depends, FastAPI
import pika 
from app.routers import auth , ondc
from app.local_database.database import Base , engine

app = FastAPI()


# rabbitmq connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue='email_notification')
Base.metadata.create_all(engine)
app.include_router(auth.router)
app.include_router(ondc.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}