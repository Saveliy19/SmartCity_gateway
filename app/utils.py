import aiohttp
from fastapi import HTTPException
import json

from app.rmq import RabbitMQManager

rabbitmq_manager = RabbitMQManager()

async def send_to_get_data(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data.dict()) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status)
            return await response.json()
        
async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # Проверка успешности запроса
            if response.status != 200:
                raise HTTPException(status_code=response.status)
            return await response.json()
        

async def send_notification_by_email(emails: list, subject:str, content: str):
    data = {
    'email_addresses': emails,
    'subject': subject,
    'message': content
    }
    message_data = json.dumps(data)
    rabbitmq_manager.send_message('notification_queue', message_data)