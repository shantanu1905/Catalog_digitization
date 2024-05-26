from sentence_transformers import SentenceTransformer
import numpy as np
import psycopg2
import json
import pandas as pd
import psycopg2
from psycopg2.extras import Json
text_model =  SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=postgres")

def text_embedding(text):
        query_embedding =  text_model.encode([text])
        return query_embedding


# Function to add a new product with image embedding to PostgreSQL
def add_product_to_postgres(name, image_url, ean, brand, category, price ,description ,conn):
  
    
    text_embed = text_embedding(name)

    # Convert the embedding to a list for storage
    text_embed_list = text_embed[0].tolist()
   
    # Example: Connect to PostgreSQL and add a product
    conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=postgres")

    # Define the SQL query without specifying product_id
    sql = """
    INSERT INTO retailproducts (name, image_url, ean, brand, category, price ,description , name_embedding)
    VALUES (%s, %s, %s, %s, %s, %s,%s,%s)
    RETURNING id;
    """


    # Execute the query
    with conn.cursor() as cur:
        cur.execute(sql, (name, image_url, ean, brand, category,price,description, Json(text_embed_list)))

        # Retrieve the automatically generated product_id
        product_id = cur.fetchone()[0]

    # Commit the transaction
    conn.commit()

    return product_id


df = pd.read_csv("latest_products.csv")
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
    ean = ean,
    brand = brand,
    description= description,
    price=price,
    image_url= image_url,
    category=category,
    conn=conn
)

    print(f"Automatically generated product_id: {generated_product_id}")