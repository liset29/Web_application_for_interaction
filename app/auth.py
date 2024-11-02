import bcrypt
import jwt
import config as con
from datetime import timedelta, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

from app.db_helper import db_helper
from app.schemes import UserModel
from app.utils_users import get_user



http_bearer = HTTPBearer()


async def encode_jwt(payload: dict,
                     private_key: str = con.private_key,
                     algorithm: str = con.algorithm,
                     expire_minutes: int = con.access_token_expire,
                     expire_timedelta: timedelta | None = None):
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=int(expire_minutes))
    to_encode.update(
        exp=expire,
        iat=now)
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


async def decode_jwt(token: str,
                     public_key: str = con.public_key,
                     algorithm=con.algorithm):
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


async def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


async def validate_password(password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password)




async def get_curresnt_token_payload(
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
):
    token = credentials.credentials
    try:
        payload = await decode_jwt(token=token)
    except InvalidTokenError:

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'invalid token error')
    return payload


async def get_curresnt_auth_user(
        payload: dict = Depends(get_curresnt_token_payload),
        session: AsyncSession = Depends(db_helper.scoped_session_dependency)
) :
    username: str | None = payload.get('sub')

    user = await get_user(username, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid token or user not found')

    return user


async def get_curresnt_active_auth_user(
        user: UserModel = Depends(get_curresnt_auth_user)
):
    if user.is_active:
        return user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail='user inactive')