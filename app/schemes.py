from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr

from const import LATEST, EARLIEST, MALE, FEMALE


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


class SortByRegistrationEnum(str, Enum):
    latest = LATEST
    earliest = EARLIEST


class GenderEnum(str, Enum):
    male = MALE
    female = FEMALE


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
    latitude: float
    longitude: float


class UserResponse(BaseModel):
    id: int | None
    first_name: str | None
    last_name: str | None
    gender: GenderEnum | None
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}

class UserFilter(BaseModel):
    gender: Optional[GenderEnum] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    sort_by_registration: Optional[SortByRegistrationEnum] = None
    max_distance: Optional[float] = None

class RateResponse(BaseModel):
    message: str
    email: Optional[str] = None