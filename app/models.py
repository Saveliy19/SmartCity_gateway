from pydantic import BaseModel, EmailStr

class UserToLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str

class UserToRegistrate(BaseModel):
    email: EmailStr
    password: str
    last_name: str
    first_name: str
    patronymic: str
    rating: float
    is_moderator: bool
    city: int