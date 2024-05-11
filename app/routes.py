from fastapi import APIRouter, HTTPException, status
import aiohttp
import asyncio

from app.models import UserToLogin, Token, UserToRegistrate, UserID, UserToFrontend, PetitionsCity, City, PetitonID, PetitionData, LikeIn, LikeOut, SubjectForBriefAnalysis
from app.models import PetitionWithToken, OutputPetition, PetitionStatus, PetitionStatusOutput
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

# маршрут для получения данных админа
'''@router.post("/get_admin_data")
async def get_admin_data(token: Token):'''


# маршрут для создания новой петиции
@router.post("/make_petition")
async def make_petition(content: PetitionWithToken):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = content.token))
        if result:
            output_petition = OutputPetition(header = content.header,
                                            is_initiative = content.is_initiative,
                                            category = content.category,
                                            petition_description = content.description,
                                            address = content.address,
                                            region = content.region,
                                            city_name = content.city_name,
                                            petitioner_id = result[0]["id"])
            print(output_petition)
            await send_to_get_data(PETITION_SERVICE_ADDRESS + '/make_petition', output_petition)
            return status.HTTP_200_OK
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    
# маршрут для проверки лайка пользователя на записи
@router.post("/check_like")
async def check_like(like: LikeIn):
    try:
        user = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = like.user_token))
        if user:
            result = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/check_like', LikeOut(user_id = user[0]["id"], petition_id=like.petition_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
    
# маршрут для обновления статуса заявки
@router.post("/update_petition")
async def update_petition(petition: PetitionStatus):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = petition.user_token))
        if result:
            if result[0]["is_moderator"] == True:
                await send_to_get_data(PETITION_SERVICE_ADDRESS + '/update_petition_status', PetitionStatusOutput(id=petition.id, 
                                                                                                                  status=petition.status, 
                                                                                                                  comment=petition.comment,
                                                                                                                  admin_id=result[0]["id"]))
                return status.HTTP_200_OK
            else:
                return status.HTTP_403_FORBIDDEN
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# маршрут для получения краткой аналитики по населенному пункту
@router.post("/get_brief_analysis")
async def get_brief_analysis(subject: SubjectForBriefAnalysis):
    try:
        result = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_brief_analysis', subject)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))