import pika
import json

from app.config import RMQ_NAME, RMQ_PASSWORD


class RabbitMQManager:
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
        self.credentials = pika.PlainCredentials(RMQ_NAME, RMQ_PASSWORD)
        self._connect()

    def _connect(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=self.credentials))
        self.channel = self.connection.channel()

    def _reconnect(self):
        self.close_connection()
        self._connect()

    def send_message(self, queue_name, data):
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(exchange='',
                                       routing_key=queue_name,
                                       body=data)
            print(f" [x] Sent message '{data}' to queue '{queue_name}'")
        except (pika.exceptions.ConnectionClosed, AttributeError):
            print(" [!] Connection to RabbitMQ closed. Reconnecting...")
            self._reconnect()
            self.send_message(queue_name, data)

    def close_connection(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def __del__(self):
        self.close_connection()
