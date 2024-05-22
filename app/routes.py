from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from typing import List
import aiohttp

from app.logging import logging

import base64
from app.models import (UserToLogin, Token, UserToRegistrate, UserEmail, UserToFrontend, PetitionsCity,
                        CityWithType, PetitonID, PetitionData, LikeIn, LikeOut, SubjectForBriefAnalysis,
                        OutputPetition, PetitionStatus, PetitionStatusOutput, AdminToFrontend, AdminPetitions,
                          City, Photo, DataForDetailedAnalysis, RegionForDetailedAnalysis)
from app.utils import send_to_get_data, send_notification_by_email, fetch_data
from app.config import CLIENT_SERVICE_ADDRESS, PETITION_SERVICE_ADDRESS

router = APIRouter()

# маршрут для регистрации нового пользователя в системе
@router.post("/registration")
async def registrate_new_user(user: UserToRegistrate):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/registration', user)
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    if result:
        await send_notification_by_email([user.email], 'Регистрация в системе "Умный город"', f'{user.first_name}, поздравляем Вас с успешной регистрацией в системе "Умный город!"')
    return result

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
        user_petitions = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_petitions', UserEmail(email=user_info[0]["email"]))
        user_petitions_list = user_petitions[0]["petitions"]
    except aiohttp.ClientError:
        # Если сервис петиций не отвечает, то список заявок пользователя пуст
        user_petitions_list = []
    return UserToFrontend(id = user_info[0]["id"],
                          email = user_info[0]["email"],
                          last_name = user_info[0]["last_name"],
                          first_name = user_info[0]["first_name"],
                          patronymic = user_info[0]["patronymic"],
                          rating = user_info[0]["rating"],
                          city = user_info[0]["city"],
                          region = user_info[0]["region"],
                          petitions = user_petitions_list)

# получение списка городов
@router.get("/get_cities")
async def get_citites():
    try:
        print(CLIENT_SERVICE_ADDRESS + '/get_citites')
        citites_per_region = await fetch_data(CLIENT_SERVICE_ADDRESS + '/get_cities')
        if citites_per_region:
            return citites_per_region
    except:
        raise HTTPException(status_code=500)


# маршрут для получения данных админа
@router.post("/get_admin_data")
async def get_admin_data(token: Token):
    try:
        admin_info = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/get_data', token)
    except aiohttp.ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return AdminToFrontend(id = admin_info[0]["id"],
                          email = admin_info[0]["email"],
                          last_name = admin_info[0]["last_name"],
                          first_name = admin_info[0]["first_name"],
                          patronymic = admin_info[0]["patronymic"],
                          city = admin_info[0]["city"],
                          region = admin_info[0]["region"])


# маршрут для создания новой петиции
@router.post("/make_petition")
async def make_petition(header: str = Form(...),
                        is_initiative: bool = Form(...),
                        category: str = Form(...),
                        description: str = Form(...),
                        address: str = Form(...),
                        city_name: str = Form(...),
                        photos: List[UploadFile] = File(...),
                        token: str = Form(...),
                        region: str = Form(...)):
    files = [Photo(filename=p.filename, content=base64.b64encode(await p.read()).decode('utf-8')) for p in photos]
    #try:
    result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = token))
    print(result)
    if result:
        output_petition = OutputPetition(header = header,
                                        is_initiative = is_initiative,
                                        category = category,
                                        petition_description = description,
                                        address =address,
                                        region = region,
                                        city_name = city_name,
                                        petitioner_email = result[0]["email"],
                                        photos = files)
        await send_to_get_data(PETITION_SERVICE_ADDRESS + '/make_petition', output_petition)
        return status.HTTP_200_OK
    #except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))

'''@router.get("/images/{image_path:path}")
async def get_image(image_path: str):
    result = await get_image_from_service(PETITION_SERVICE_ADDRESS + '/images')
    return result'''


# маршрут для получения списка петиций в городе
@router.post("/get_city_petitions")
async def get_city_petitions(city: CityWithType):
    try:
        result = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_city_petitions', city)
        petitions = result[0]["petitions"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return PetitionsCity(petitions = petitions), status.HTTP_200_OK
    
# маршрут для получения списка петиций по админскому токену и городу
@router.post("/get_admin_petitions")
async def get_admin_petitions(data: AdminPetitions):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = data.token))
        if result:
            if result[0]["is_moderator"] == True:
                petitions = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_admins_city_petitions', City(region=data.region, name=data.city_name))
            else:
                return status.HTTP_403_FORBIDDEN
        if petitions:
            return petitions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
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
                        petitioner_email = data["petitioner_email"],
                        submission_time = data["submission_time"],
                        address = data["address"],
                        region = data["region"],
                        city_name = data["city_name"],
                        likes_count = data["likes_count"],
                        comments = data["comments"],
                        photos = data["photos"]), status.HTTP_200_OK

# маршрут для установки или отмены лайка на запись
@router.post("/like_petition")
async def like_petition(like: LikeIn):
    try:
        user = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = like.user_token))
        if user:
            await send_to_get_data(PETITION_SERVICE_ADDRESS + '/like_petition', LikeOut(user_email = user[0]["email"], petition_id=like.petition_id))
            return status.HTTP_200_OK
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# маршрут для проверки лайка пользователя на записи
@router.post("/check_like")
async def check_like(like: LikeIn):
    try:
        user = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = like.user_token))
        if user:
            result = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/check_like', LikeOut(user_email = user[0]["email"], petition_id=like.petition_id))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result
    
# маршрут для обновления статуса заявки
@router.post("/update_petition")
async def update_petition(petition: PetitionStatus):
    try:
        user = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = petition.user_token))
        if user:
            if user[0]["is_moderator"] == True:
                emails = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/update_petition_status', PetitionStatusOutput(id=petition.id, 
                                                                                                                  status=petition.status, 
                                                                                                                  comment=petition.comment,
                                                                                                                  admin_id=user[0]["id"]))
            else:
                return status.HTTP_403_FORBIDDEN
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    await send_notification_by_email(emails[0]["petitioner_emails"], f'Обновление статуса заявки №{petition.id}:',  f' Новый статус завки - {petition.status.upper()}')
    return status.HTTP_200_OK

# маршрут для обновления статуса заявки
@router.post("/get_detailed_analysis")
async def get_detailed_analysis(data: DataForDetailedAnalysis):
    try:
        result = await send_to_get_data(CLIENT_SERVICE_ADDRESS + '/verify_user', Token(token = data.user_token))
        if result:
            if result[0]["is_moderator"] == True:
                Analysis = await send_to_get_data(PETITION_SERVICE_ADDRESS + '/get_detailed_analysis', RegionForDetailedAnalysis(region_name=data.region_name,
                                                                                                                              city_name=data.city_name,
                                                                                                                              start_time=data.start_time,
                                                                                                                              end_time=data.end_time,
                                                                                                                              rows_count=data.rows_count))
                return Analysis
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