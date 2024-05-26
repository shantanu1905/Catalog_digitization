from sqlalchemy.orm import Session
import app.local_database.schemas as _schemas
from sqlalchemy import text
import app.local_database.models as _models




def search_by_embedding(embeddings: list, db: Session):
    # Assuming `embeddings` is a list and needs to be converted to a format for the query
    text_embed_list = str(embeddings).replace('[', '{').replace(']', '}')
    
    # Define the SQL query using SQLAlchemy text construct
    sql = text(f"SELECT * FROM retailproducts ORDER BY name_embedding <-> '{embeddings}' LIMIT 3;")
    print(sql)
    
    # Execute the query with the SQLAlchemy session
    result = db.execute(sql).fetchone()
    
    if result:
        product_details = {
            'id': result[0],
            "name": result[1],
            'image_url': result[2],
            'ean': result[3],
            'brand': result[4],
            'category': result[5],
            'price': result[6],
            'description': result[7]
        }
        return product_details
    else:
        return None