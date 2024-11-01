from enum import Enum

from pydantic import BaseModel, EmailStr


class TokenInfo(BaseModel):
    access_token: str
    token_type: str

class GenderEnum(str, Enum):
    male = "мужской"
    female = "женский"
class UserModel(BaseModel):
    email: EmailStr
    username: str
    first_name : str
    last_name : str
    gender: GenderEnum


    class Config:
        from_attributes = True


class UserModelCreated(UserModel):
    password: str