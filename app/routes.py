from fastapi import APIRouter, HTTPException, status
import aiohttp

from app.models import UserToLogin, Token, UserToRegistrate
from app.utils import send_to_get_data
from app.config import CLIENT_SERVICE_ADDRESS

router = APIRouter()

# маршрут для регистрации нового пользователя в системе
@router.post("/registration")
async def registrate_new_user(user: UserToRegistrate):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/registration', user)
        return result
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail="Error communicating with the destination service")

#  маршрут для авторизации и получения jwt токена
@router.post("/login")
async def login(user: UserToLogin):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/token', user)
        return result
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail="Error communicating with the destination service")
    
# маршрут личного кабинета пользователя
@router.post("/me")
async def get_information_about_user(token: Token):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/get_data', token)
        return result
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail="Error communicating with the destination service")