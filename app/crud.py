import base64

from app.auth import encode_jwt
from app.models import UserModel
from app.schemes import UserModelCreated
from app.utils_users import check_unique_value, hash_password


async def registration(user: UserModelCreated,avatar,session):
    async with session() as session:
        await check_unique_value(session, user)
        password = await hash_password(user.password)
        password = base64.b64encode(password).decode('utf-8')

        new_user = UserModel(
            username=user.username,
            email=user.email,
            password=password,
            avatar=avatar,
            gender=user.gender,
            first_name=user.first_name,
            last_name=user.last_name
        )
        session.add(new_user)
        await session.commit()

        jwt_payload = {
            'sub': user.username,
            'email': user.email
        }

        await encode_jwt(jwt_payload)

        await session.commit()

        return new_user