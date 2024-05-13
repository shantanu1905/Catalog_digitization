# rabbitmq.py
import pika

class RabbitMQ:
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(self.host, self.port, '/', credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def publish(self, exchange, routing_key, body):
        self.channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body)

    def consume(self, queue, callback):
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

# Create a singleton instance of RabbitMQ
rabbitmq = RabbitMQ()

# Optionally, you can add a function to initialize the RabbitMQ connection
def initialize_rabbitmq(host='localhost', port=5672, username='guest', password='guest'):
    rabbitmq.host = host
    rabbitmq.port = port
    rabbitmq.username = username
    rabbitmq.password = password
    rabbitmq.connect()
