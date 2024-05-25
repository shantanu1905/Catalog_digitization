# import app.local_database.database import get_db
# import app.local_database.schemas as _schemas
# import app.local_database.models as _models


# def search_by_embedding(embeddings , db):
    
#     # Example: Connect to PostgreSQL and add a product
#     conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=password")

#     # Define the SQL query without specifying product_id
#     sql = f"""
#     SELECT * FROM Products ORDER BY name_embedding <-> '{text_embed_list}' LIMIT 1;
#     """
#     # Execute the query
#     with conn.cursor() as cur:
#         cur.execute(sql)
#         result = cur.fetchone()

#     product_details = {
#                     'id':result[0],
#                     "name":result[1],
#                     'image_url':result[2],
#                     'ean':result[3],
#                     'brand':result[4],
#                     'category':result[5],
#                     'price':result[6],
#                     'description':result[7]
#                     }
#     # Commit the transaction
#     conn.commit()

#     return product_details

