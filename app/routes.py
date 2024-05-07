from fastapi import APIRouter, HTTPException, status
import aiohttp
import asyncio

from app.models import UserToLogin, Token, UserToRegistrate, UserID, UserToFrontend, PetitionsCity, City, PetitonID, PetitionData, LikeIn, LikeOut, SubjectForBriefAnalysis
from app.utils import send_to_get_data
from app.config import CLIENT_SERVICE_ADDRESS, PETITION_SERVICE_ADDRESS

router = APIRouter()

# маршрут для регистрации нового пользователя в системе
@router.post("/registration")
async def registrate_new_user(user: UserToRegistrate):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/registration', user)
        return result
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

#  маршрут для авторизации и получения jwt токена
@router.post("/login")
async def login(user: UserToLogin):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/token', user)
        return result
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# маршрут личного кабинета пользователя
@router.post("/me")
async def get_information_about_user(token: Token):
    try:
        user_info = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/get_data', token)
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    try:
        user_petitions = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_petitions', UserID(id=user_info[0]["id"]))
        user_petitions_list = user_petitions[0]["petitions"]
    except aiohttp.ClientError:
        # Если сервис петиций не отвечает, то список заявок пользователя пуст
        user_petitions_list = []
    return UserToFrontend(id = user_info[0]["id"],
                          last_name = user_info[0]["last_name"],
                          first_name = user_info[0]["first_name"],
                          patronymic = user_info[0]["patronymic"],
                          rating = user_info[0]["rating"],
                          city = user_info[0]["city"],
                          region = user_info[0]["region"],
                          petitions = user_petitions_list)

# маршрут для получения списка петиций в городе
@router.post("/get_city_petitions")
async def get_city_petitions(city: City):
    try:
        result = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_city_petitions', city)
        petitions = result[0]["petitions"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return PetitionsCity(petitions = petitions), status.HTTP_200_OK
    
        
# маршрут для получения полной информации по петиции
@router.post("/get_petition_data")
async def get_petition_data(petiton: PetitonID):
    try:
        result = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_petition_data', petiton)
        data = result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return PetitionData(id = data["id"], 
                        header = data["header"], 
                        is_initiative = data["is_initiative"], 
                        category = data["category"],
                        description = data["description"],
                        status = data["status"],
                        petitioner_id = data["petitioner_id"],
                        submission_time = data["submission_time"],
                        address = data["address"],
                        region = data["region"],
                        city_name = data["city_name"],
                        likes_count = data["likes_count"]), status.HTTP_200_OK

# маршрут для установки или отмены лайка на запись
@router.post("/like_petition")
async def like_petition(like: LikeIn):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = like.user_token))
        if result:
            await send_to_get_data(PETITION_SERVICE_ADDRESS + '/like_petition', LikeOut(user_id = result[0]["id"], petition_id=like.petition_id))
            return status.HTTP_200_OK
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# маршрут для обновления статуса заявки

# маршрут для получения краткой аналитики по населенному пункту
@router.post("/get_brief_analysis")
async def get_brief_analysis(subject: SubjectForBriefAnalysis):
    try:
        result = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_brief_analysis', subject)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))