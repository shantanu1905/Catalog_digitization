import json
import base64
import pandas as pd
import easyocr
import pika


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
