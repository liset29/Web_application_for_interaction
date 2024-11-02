from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


class SortByRegistrationEnum(str, Enum):
    latest = "Последние зарегистрированные"
    earliest = "Ранее зарегистрированные"


class GenderEnum(str, Enum):
    male = "мужской"
    female = "женский"


class UserModel(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    gender: GenderEnum

    class Config:
        from_attributes = True


class UserModelCreated(UserModel):
    password: str


class UserResponse(BaseModel):
    id: int | None
    first_name: str | None
    last_name: str | None
    gender: GenderEnum | None
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
