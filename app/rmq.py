import pika
from pika.exceptions import StreamLostError
import time
import logging

from app.config import RMQ_NAME, RMQ_PASSWORD

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RabbitMQManager:
    def __init__(self, host='localhost'):
        self.host = host
        self.connection = None
        self.channel = None
        self.credentials = pika.PlainCredentials(RMQ_NAME, RMQ_PASSWORD)
        self._connect()

    def _connect(self):
        """Попытка установить соединение с RabbitMQ."""
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=self.credentials))
            self.channel = self.connection.channel()
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None

    def _reconnect(self, retries=5, delay=5):
        """Попытка повторного подключения к RabbitMQ в случае сбоя соединения.
        
        Аргументы:
        retries (int): количество попыток повторного подключения.
        delay (int): задержка между попытками повторного подключения в секундах.
        """
        for attempt in range(retries):
            try:
                logger.info(f"Attempting to reconnect to RabbitMQ (Attempt {attempt + 1}/{retries})")
                self._connect()
                if self.connection and self.connection.is_open:
                    logger.info("Reconnected to RabbitMQ")
                    return
            except Exception as e:
                logger.error(f"Reconnect attempt failed: {e}")
            time.sleep(delay)
        raise Exception("Failed to reconnect to RabbitMQ after several attempts")

    def send_message(self, queue_name, data):
        """Отправка сообщения в указанную очередь RabbitMQ.
        
        Аргументы:
        queue_name (str): имя очереди.
        data (str): данные для отправки.
        """
        if not self.connection or self.connection.is_closed or not self.channel:
            logger.warning("Connection to RabbitMQ is closed. Trying to reconnect...")
            self._reconnect()
        
        try:
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.channel.basic_publish(exchange='',
                                       routing_key=queue_name,
                                       body=data)
            logger.info(f" [x] Sent message '{data}' to queue '{queue_name}'")
        except StreamLostError as e:
            logger.warning(f"Connection closed while sending message. Reconnecting and retrying: {e}")
            self._reconnect()
            self.send_message(queue_name, data)
        except Exception as e:
            logger.error(f"Failed to send message to RabbitMQ: {e}")
            raise

    def close_connection(self):
        """Закрытие соединения с RabbitMQ, если оно открыто."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed connection to RabbitMQ")

    def __del__(self):
        """Закрытие соединения при удалении объекта RabbitMQManager."""
        self.close_connection()
