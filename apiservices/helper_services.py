from bs4 import BeautifulSoup
import httpx
from fastapi import FastAPI ,Depends ,status ,Response ,HTTPException
import json
from fastapi.responses import JSONResponse
import psycopg2
import os 

# Retrieve environment variables
postgres_host = os.environ.get("POSTGRES_HOST")
postgres_db = os.environ.get("POSTGRES_DB")
postgres_user = os.environ.get("POSTGRES_USER")
postgres_password = os.environ.get("POSTGRES_PASSWORD")



#conn = psycopg2.connect("host=postgres_host dbname=postgres user=postgres password=password")


# Establish PostgreSQL connection
conn = psycopg2.connect(
    host=postgres_host,
    dbname=postgres_db,
    user=postgres_user,
    password=postgres_password
)

#Imports for image processing
# from tensorflow.keras.applications.resnet50 import ResNet50,preprocess_input, decode_predictions
# from tensorflow.keras.preprocessing import image
import numpy as np
import pandas as pd
import cv2
from tqdm.auto import tqdm
import os
import shutil
from matplotlib import pyplot as plt

# Text Embedding import
from sentence_transformers import SentenceTransformer, util
text_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")


#keras ocr pipeline and imports
import keras_ocr
keras_pipeline = keras_ocr.pipeline.Pipeline()

#Speech Recognition imports
import speech_recognition as sr
from typing import Union

async def scrape_upc(upc_number: str ):
    url = f"https://go-upc.com/search?q={upc_number}"
    print(url)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extracting information
        product_name = soup.find('h1', class_='product-name').text
        image_source = soup.find('figure', class_='product-image').find('img')['src']
        ean = soup.find('td', class_='metadata-label', text='EAN').find_next('td').text
        brand = soup.find('td', class_='metadata-label', text='Brand').find_next('td').text
        category = soup.find('td', class_='metadata-label', text='Category').find_next('td').text

        data = {
            'name' : product_name,
            'image_url' : image_source,
            'ean' : ean,
            'brand' : brand,
            'category' : category
        }
        #print(data)
     
        return data

    except Exception as e:
        # Handle exceptions here
        print(f"Sorry, we were not able to find a product for EAN {upc_number}")
        # raise HTTPException(status_code=500, detail="Internal Server Error")




# Function to return image embedding using ResNet50
        
# model = ResNet50(include_top=False, weights='imagenet', pooling='avg')
# def return_image_embedding(model, img_path):
#     img = image.load_img(img_path, target_size=(224, 224))
#     x = image.img_to_array(img)
#     x = np.expand_dims(x, axis=0)
#     x = preprocess_input(x)
#     embedding = model.predict(x)
#     return embedding.flatten()



# Define the path to the images folder
IMAGES_FOLDER = "images"
# Create the images folder if it doesn't exist
os.makedirs(IMAGES_FOLDER, exist_ok=True)
# Function to delete the previous image
def delete_previous_image():
    for filename in os.listdir(IMAGES_FOLDER):
        file_path = os.path.join(IMAGES_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")


            
def text_embedding(text_model, text):
    query_embedding = text_model.encode(text)
    return query_embedding


def keras_ocrr(keras_pipeline , image_path):
    results = keras_pipeline.recognize([image_path])
    df = pd.DataFrame(results[0],columns = ['text' , 'bbox'])
    words =df['text'].tolist()
    sentence = ' '.join(words)
    return sentence

def search_by_embedding(image_url):
    #embedding = return_image_embedding(model, image_url)
    ocr_text = keras_ocrr(keras_pipeline ,image_url )
    text_embed = text_embedding(text_model ,ocr_text )

    # Convert the embedding to a list for storage
    text_embed_list = text_embed.tolist()
    #embedding_list = embedding.tolist()
    
    # Example: Connect to PostgreSQL and add a product
    conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=password")

    # Define the SQL query without specifying product_id
    sql = f"""
    SELECT * FROM Products ORDER BY name_embedding <-> '{text_embed_list}' LIMIT 1;
    """
    # Execute the query
    with conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchone()

    product_details = {
                    'id':result[0],
                    "name":result[1],
                    'image_url':result[2],
                    'ean':result[3],
                    'brand':result[4],
                    'category':result[5],
                    'price':result[6],
                    'description':result[7]
                    }
    # Commit the transaction
    conn.commit()

    return product_details

def search_by_embedding_voice(audio_file):
    audio_to_text = recognize_speech(audio_file)
    print(f"Voice input given by user: {audio_to_text}")
    
    text_embed = text_embedding(text_model,audio_to_text)

    # Convert the embedding to a list for storage
    text_embed_list = text_embed.tolist()
    #embedding_list = embedding.tolist()
    
    # Example: Connect to PostgreSQL and add a product
    conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=password")

    # Define the SQL query without specifying product_id
    sql = f"""
    SELECT * FROM Products ORDER BY name_embedding <-> '{text_embed_list}' LIMIT 5;
    """
    # Execute the query
    with conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchone()

    product_details = {
                    'id':result[0],
                    "name":result[1],
                    'image_url':result[2],
                    'ean':result[3],
                    'brand':result[4],
                    'category':result[5],
                    'price':result[6],
                    'description':result[7]
                    }
    # Commit the transaction
    conn.commit()

    return product_details
def recognize_speech(audio_file_path: str) -> Union[str, dict]:
    # Create a recognizer object
    r = sr.Recognizer()

    # Read the audio file
    with sr.AudioFile(audio_file_path) as source:
        audio_data = r.record(source)  # Read the entire audio file

    # Recognize speech using Sphinx
    try:
        recognized_text =  r.recognize_google(audio_data)
        return recognized_text
    except sr.UnknownValueError:
        return {"error": "Sphinx could not understand the audio"}
    except sr.RequestError as e:
        return {"error": f"Sphinx error: {e}"}