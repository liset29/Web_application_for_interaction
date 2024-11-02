import base64

from fastapi import HTTPException
from sqlalchemy import select, asc, desc
from starlette import status

from app.auth import encode_jwt
from app.models import UserModel, Rating
from app.schemes import UserModelCreated
from app.utils_rating import check_daily_limit, send_email
from app.utils_users import check_unique_value, hash_password


async def registration(user: UserModelCreated, avatar, session):
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


async def rate_the_user(user_id, rater, session):
    rater_id = rater.id
    if not await  check_daily_limit(rater_id, session):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Превышен дневной лимит оценок."
        )
    rated_user = await session.execute(select(UserModel).where(UserModel.id == user_id))
    if not rated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден.")
    rated_user = rated_user.scalars().first()
    if rater_id == rated_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя оценивать самого себя.")

    await add_rating(rater_id, rated_user, session)

    stmt = select(Rating).where(
        Rating.rater_id == rated_user.id,
        Rating.rated_id == rater_id
    )

    result = await session.execute(stmt)
    mutual_rating = result.scalars().first()
    if mutual_rating:
        await send_email(
            [{'email_rater': rater.email, 'username_rated': rated_user.username, 'email_rated': rated_user.email},
             {'email_rater': rated_user.email, 'username_rated': rater.username, 'email_rated': rater.email}])
        return {"message": "Взаимная симпатия обнаружена!", 'email': rated_user.email}
    return 'Пользователь был оценён'


async def add_rating(rater_id, rated_user, session):
    stmt = select(Rating).where(
        Rating.rater_id == rater_id,
        Rating.rated_id == rated_user.id

    )
    result = await session.execute(stmt)
    existing_rating = result.scalars().first()
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Оценка уже была добавлена.")
    rating = Rating(rater_id=rater_id, rated_id=rated_user.id)
    session.add(rating)
    await session.commit()


async def get_all_users(gender,first_name,last_name,sort_by_registration,session):
    query = select(UserModel)

    if gender:
        query = query.filter(UserModel.gender == gender)
    if first_name:
        query = query.filter(UserModel.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(UserModel.last_name.ilike(f"%{last_name}%"))

    if sort_by_registration == "Последние зарегистрированные":
        query = query.order_by(asc(UserModel.created_at))
    elif sort_by_registration == "Ранее зарегистрированные":
        query = query.order_by(desc(UserModel.created_at))

    result = await session.execute(query)
    users = result.scalars().all()
    return users