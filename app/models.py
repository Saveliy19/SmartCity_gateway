from pydantic import BaseModel, EmailStr
from typing import List
from fastapi import File, UploadFile

class UserToLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str

class UserEmail(BaseModel):
    email: EmailStr

# класс с краткой информации о петиции
class PetitionWithHeader(BaseModel):
    id: int
    header: str
    status: str
    address: str
    date: str
    likes: int

class PetitionsCity(BaseModel):
    petitions: List[PetitionWithHeader]

class UserToFrontend(BaseModel):
    id: int
    email: EmailStr
    last_name: str
    first_name: str
    patronymic: str
    rating: float
    city: str
    region: str
    petitions: List[PetitionWithHeader]

class AdminToFrontend(BaseModel):
    id: int
    email: EmailStr
    last_name: str
    first_name: str
    patronymic: str
    city: str
    region: str

class Photo(BaseModel):
    filename: str
    content: str

class UserToRegistrate(BaseModel):
    email: EmailStr
    password: str
    last_name: str
    first_name: str
    patronymic: str
    city: int

class City(BaseModel):
    region: str
    name: str

class CityWithType(City):
    is_initiative: bool

class PetitonID(BaseModel):
    id: int

class Comment(BaseModel):
    date: str
    data: str

# класс для возврата полной информации по заявке
class PetitionData(BaseModel):
    id: int
    header: str
    is_initiative: bool
    category: str
    description: str
    status: str
    petitioner_email: str
    submission_time: str
    address: str
    likes_count: int
    region: str
    city_name: str
    comments: List[Comment]
    photos: List[str]

class LikeIn(BaseModel):
    user_token: str
    petition_id: int

class LikeOut(BaseModel):
    user_email: EmailStr
    petition_id: int

class SubjectForBriefAnalysis(City):
    period: str

class AdminPetitions(BaseModel):
    token: str
    region: str
    city_name: str



# класс для обновления статуса заявки
class PetitionStatus(BaseModel):
    id: int
    user_token: str
    status: str
    comment: str

# класс для обновления статуса заявки
class PetitionStatusOutput(BaseModel):
    status: str
    id: int
    admin_id: int
    comment: str

class PetitionWithToken(BaseModel):
    token: str
    header: str
    is_initiative: bool
    category: str
    description: str
    address: str
    region: str
    city_name: str
    photo: bytes
    



class OutputPetition(BaseModel):
    header: str
    is_initiative: bool
    category: str
    petition_description: str
    address: str
    region: str
    city_name: str
    petitioner_email: EmailStr
    photos: List[Photo]

class RegionForDetailedAnalysis(BaseModel):
    region_name: str
    city_name: str
    start_time: str
    end_time: str
    rows_count: int

class DataForDetailedAnalysis(RegionForDetailedAnalysis):
    user_token: str