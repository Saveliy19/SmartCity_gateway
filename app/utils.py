import aiohttp
from fastapi import HTTPException

from app.rmq import RabbitMQManager

rabbitmq_manager = RabbitMQManager()

async def send_to_get_data(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data.dict()) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status)
            return await response.json()
        

async def send_notification_by_email(email: str, subject:str, content: str):
    message_data = f'{email},{subject},{content}'
    rabbitmq_manager.send_message('notification_queue', message_data)