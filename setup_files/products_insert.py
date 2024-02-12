import psycopg2
from psycopg2.extras import Json
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
import pandas as pd
from PIL import Image
import requests
import io

model = ResNet50(include_top=False, weights='imagenet', pooling='avg')
# Example: Connect to PostgreSQL and add a product
conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=password")

# Text Embedding import
from sentence_transformers import SentenceTransformer, util
text_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

#keras ocr pipeline and impors
import keras_ocr
keras_pipeline = keras_ocr.pipeline.Pipeline()



def text_embedding(text_model , text):
    query_embedding = text_model.encode(text)
    return query_embedding


def keras_ocr(keras_pipeline , image_path):
    results = keras_pipeline.recognize([image_path])
    df = pd.DataFrame(results[0],columns = ['text' , 'bbox'])
    words =df['text'].tolist()
    sentence = ' '.join(words)
    return sentence



# Function to return image embedding using ResNet50
def return_image_embedding(model, img_path):
    # Download the image
    response = requests.get(img_path)
    img = Image.open(io.BytesIO(response.content))

    # Resize the image to (224, 224) if needed
    img = img.resize((224, 224))

    # Convert image to array and preprocess for ResNet50
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    # Get the embedding using the provided ResNet50 model
    embedding = model.predict(x)
    return embedding.flatten()


# def return_image_embedding(model, img_path):
#     img = image.load_img(img_path, target_size=(224, 224))
#     x = image.img_to_array(img)
#     x = np.expand_dims(x, axis=0)
#     x = preprocess_input(x)
#     embedding = model.predict(x)
#     return embedding.flatten()


# Function to add a new product with image embedding to PostgreSQL
def add_product_to_postgres(name, description, price, image_url, category, conn):
    # Load the image and get the embedding using ResNet50
    embedding = return_image_embedding(model, image_url)
    text_embed = text_embedding(text_model , name)

    # Convert the embedding to a list for storage
    text_embed_list = text_embed.tolist()
    embedding_list = embedding.tolist()

    # Example: Connect to PostgreSQL and add a product
    conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=password")

    # Define the SQL query without specifying product_id
    sql = """
    INSERT INTO products (name, description, price, image_url, category, embedding ,name_embedding)
    VALUES (%s, %s, %s, %s, %s, %s,%s)
    RETURNING id;
    """


    # Execute the query
    with conn.cursor() as cur:
        cur.execute(sql, (name, description, price, image_url, category, Json(embedding_list) , Json(text_embed_list)))

        # Retrieve the automatically generated product_id
        product_id = cur.fetchone()[0]

    # Commit the transaction
    conn.commit()

    return product_id



def search_by_embedding(image_url):
    embedding = return_image_embedding(model, image_url)
    ocr_text = keras_ocr(keras_pipeline ,image_url )
    text_embed = text_embedding(text_model ,ocr_text )

    # Convert the embedding to a list for storage
    text_embed_list = text_embed.tolist()
    embedding_list = embedding.tolist()
    # Example: Connect to PostgreSQL and add a product
    conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=password")

    # Define the SQL query without specifying product_id
    sql = f"""
    SELECT * FROM Products ORDER BY embedding <-> '{embedding_list}' ,name_embedding <-> '{text_embed_list}' LIMIT 1;
    """
    # Execute the query
    with conn.cursor() as cur:
        cur.execute(sql)
        result = cur.fetchone()

    # Commit the transaction
    conn.commit()



    return result
# Close the database connection
conn.close()



df = pd.read_csv("products.csv")
df.head()

for index, row in df.iterrows():
    # Unpack values from the row
    name = row[0]
    image_url = row[1]
    ean = row[2]
    brand = row[3]
    category = row[4]
    price = row[5]
    description = str(row[6])


    generated_product_id = add_product_to_postgres(
    name=name,
    description= description,
    price=price,
    image_url= image_url,
    category=category,
    conn=conn
)

    print(f"Automatically generated product_id: {generated_product_id}")
   

