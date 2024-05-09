from pydantic import BaseModel, EmailStr
from typing import List

class UserToLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str

class UserID(BaseModel):
    id: int

# класс с краткой информации о петиции
class PetitionWithHeader(BaseModel):
    id: int
    header: str
    status: str
    address: str

class PetitionsCity(BaseModel):
    petitions: List[PetitionWithHeader]

class UserToFrontend(BaseModel):
    id: int
    last_name: str
    first_name: str
    patronymic: str
    rating: float
    city: str
    region: str
    petitions: List[PetitionWithHeader]



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
    is_initiative: bool

class PetitonID(BaseModel):
    id: int

# класс для возврата полной информации по заявке
class PetitionData(BaseModel):
    id: int
    header: str
    is_initiative: bool
    category: str
    description: str
    status: str
    petitioner_id: int
    submission_time: str
    address: str
    likes_count: int
    region: str
    city_name: str

class LikeIn(BaseModel):
    user_token: str
    petition_id: int

class LikeOut(BaseModel):
    user_id: int
    petition_id: int

class SubjectForBriefAnalysis(BaseModel):
    type: str
    name: str
    period: str


class PetitionWithToken(BaseModel):
    token: str
    header: str
    is_initiative: bool
    category: str
    description: str
    address: str
    region: str
    city_name: str

class OutputPetition(BaseModel):
    header: str
    is_initiative: bool
    category: str
    petition_description: str
    address: str
    region: str
    city_name: str
    petitioner_id: int