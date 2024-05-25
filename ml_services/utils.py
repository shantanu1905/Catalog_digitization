import json
import base64
import pandas as pd
import easyocr
import numpy as np
import pika
# Text Embedding import
from sentence_transformers import SentenceTransformer

class OCRService:
   
    def __init__(self):
        self.keras_pipeline = "dc"

    
    def easy_ocr(self,image_path):
        reader = easyocr.Reader(['en', 'es'])
        results = reader.readtext(image_path)
        words = [entry[1] for entry in results]
        sentence = ' '.join(words)
        print(sentence)
        return sentence


    def process_request(self, message):
        message_body = json.loads(message)

        file_base64 = message_body['file']
        print(f" [x]user request recieved from api..")
        print(f" [x]processing request.........")

        # Assuming file_base64 contains the base64-encoded string
        file_data = base64.b64decode(file_base64.encode())
        # Write the decoded file data to a new file
        with open('artifacts/decoded_file.png', 'wb') as f:
            f.write(file_data)

        image_path = "artifacts/decoded_file.png"
        ocr_text = self.easy_ocr(image_path)
        print(" [^]OCR processing done !!!")

        response = {
            "ocr_text": ocr_text
        }

        return response




def send_email_notification(email, ocr_text, channel):
    # Send an email notification using RabbitMQ
    message = {
        'email': email,
        'subject':'OCR Process Completed !!',
        'body':f'We are pleased to inform you that the OCR (Optical Character Recognition) process for your image has been successfully completed.\n The extracted text has been processed and is now ready for use.\n\n  OCR text : {ocr_text}',
        'other': 'null',
       }

    try:
        channel.basic_publish(
            exchange="",
            routing_key='email_notification',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
        print("Sent OCR Process Completed email notification")
    except Exception as err:
        print(f"Failed to publish message: {err}")





class EmbeddingService:
   
    def __init__(self):
        self.text_model =  SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
            
    def text_embedding(self, text):
        query_embedding =  self.text_model.encode([text])
        return query_embedding

    def process_request(self, message):
        message_body = json.loads(message)

        text = message_body['text']
        print(f" [x]user request for text embedding recieved from api..")
        print(f" [x]processing request.........")
        print()

        embed_text = self.text_embedding(text)
        print(" [^]text embedding created successfully !!!")
        print(embed_text)


        response = {
            "embeddings": embed_text
        }

        return response

def convert_ndarray_to_list(obj):
    if isinstance(obj, dict):
        return {k: convert_ndarray_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarray_to_list(i) for i in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
