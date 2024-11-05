import os

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, Query, UploadFile, File
from fastapi.security import HTTPBearer
from app import crud
from app.auth import encode_jwt, get_curresnt_active_auth_user
from app.crud import rate_the_user, get_all_users
from app.db_helper import db_helper
from app.schemes import (
    TokenInfo,
    UserModel,
    UserModelCreated,
    UserResponse,
    GenderEnum,
    SortByRegistrationEnum, UserFilter, RateResponse,
)

from app.auth_utils import validate_auth_user
from app.watermark import add_watermark_and_save
from config import AVATAR_DIR, WATERMARK_DIR

http_bearer = HTTPBearer()

users_router = APIRouter(prefix="/user", tags=["USER"])



@users_router.post(
    "/api/login",
    response_model=TokenInfo,
    description="Endpoint that issues jwt token",
    response_description="Token",
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
async def auth_user(user: UserModel = Depends(validate_auth_user)):
    jwt_payload = {"sub": user.username, "email": user.email}
    token = await encode_jwt(jwt_payload)
    return TokenInfo(access_token=token, token_type="Bearer")


@users_router.get(
    "/api/users/me",
    description="Endpoint that shows the data of users who have passed authentication",
    response_description="User",
    response_model=UserModel,
    status_code=status.HTTP_200_OK,
    response_model_by_alias=False,
)
async def auth_user_check(user: UserModel = Depends(get_curresnt_active_auth_user)):
    user = UserModel(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        gender=user.gender,
    )
    return user


@users_router.post(
    "/api/clients/create",
    description="Endpoint that creates admin",
    response_description="New user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def registration(
    user: UserModelCreated = Depends(),
    avatar: UploadFile = File(...),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    avatar_path = os.path.join(AVATAR_DIR, avatar.filename)
    await add_watermark_and_save(
        avatar, WATERMARK_DIR, avatar_path, position=(50, 50), transparency=0.5
    )
    result = await crud.registration(user=user, avatar=avatar_path, session=session)
    return result


@users_router.post("/api/clients/{id}/match",
    description="Endpoint that allows you to rate users",
    status_code=status.HTTP_201_CREATED,
    response_model= RateResponse,
    response_model_by_alias=False)
async def rate_user(
    id: int,
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
    user: UserModel = Depends(get_curresnt_active_auth_user)
):
    result = await rate_the_user(id, user, session)
    result_message = result.get("message")
    result_email = result.get("email")


    return RateResponse(message=result_message, email=result_email)


@users_router.get("/api/list",
    description="Endpoint that shows users with filtering",
    response_model=List[UserResponse],
    status_code = status.HTTP_200_OK,
    response_model_by_alias = False)
async def get_users_list(
    user: UserModel = Depends(get_curresnt_active_auth_user),
    filters: UserFilter = Depends(),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    users = await get_all_users(user, filters, session)
    return users
