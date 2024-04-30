import aiohttp
from fastapi import HTTPException


async def send_to_get_data(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data.dict()) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status)
            return await response.json()