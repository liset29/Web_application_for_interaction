import base64

from fastapi import HTTPException
from sqlalchemy import select, asc, desc, and_
from starlette import status
from app.auth import encode_jwt
from app.models import UserModel, Rating
from app.schemes import UserModelCreated, UserFilter
from app.utils import check_daily_limit, send_email, calculate_distance
from app.auth_utils import check_unique_value, hash_password
from const import SORT_BY_RECENT, SORT_BY_OLDEST


async def registration(user: UserModelCreated, avatar: str, session) -> UserModel:
    '''Создаёт нового пользователя'''
    async with session() as session:
        await check_unique_value(session, user)
        password = await hash_password(user.password)
        password = base64.b64encode(password).decode("utf-8")

        new_user = UserModel(
            username=user.username,
            email=user.email,
            password=password,
            avatar=avatar,
            gender=user.gender,
            first_name=user.first_name,
            last_name=user.last_name,
            latitude=user.latitude,
            longitude=user.longitude,
        )
        session.add(new_user)
        await session.commit()

        jwt_payload = {"sub": user.username, "email": user.email}
        await encode_jwt(jwt_payload)

        return new_user


async def rate_the_user(user_id: int, rater: UserModel, session):
    """Оценивает пользователя, проверяя лимиты и отправляя уведомления при взаимной оценке."""

    rater_id = rater.id

    await check_daily_rating_limit(rater_id, session)

    rated_user = await get_rated_user(user_id, session)

    await prevent_self_rating(rater_id, rated_user.id)

    await add_rating(rater_id, rated_user, session)

    return await check_mutual_rating_and_notify(rater, rated_user, session)


async def check_daily_rating_limit(rater_id: int, session):
    """Проверяет, достигнут ли суточный лимит оценок для пользователя."""
    if not await check_daily_limit(rater_id, session):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily rating limit exceeded.",
        )


async def get_rated_user(user_id: int, session):
    """Получает информацию о пользователе, который будет оценен."""
    rated_user_query = await session.execute(select(UserModel).where(UserModel.id == user_id))
    rated_user = rated_user_query.scalars().first()

    if not rated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return rated_user


async def prevent_self_rating(rater_id: int, rated_user_id: int):
    """Предотвращает возможность самооценки."""
    if rater_id == rated_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't evaluate yourself.",
        )


async def check_mutual_rating_and_notify(rater: UserModel, rated_user: UserModel, session):
    """Проверяет наличие взаимной оценки и отправляет уведомление, если она найдена."""
    mutual_rating_query = select(Rating).where(
        and_(
            Rating.rater_id == rated_user.id,
            Rating.rated_id == rater.id
        )
    )

    mutual_rating = await session.execute(mutual_rating_query)
    mutual_rating = mutual_rating.scalars().first()
    if mutual_rating:
        await send_email([
            {
                "email_rater": rater.email,
                "username_rated": rated_user.username,
                "email_rated": rated_user.email,
            },
            {
                "email_rater": rated_user.email,
                "username_rated": rater.username,
                "email_rated": rater.email,
            },
        ])
        return {"message": "Mutual attraction detected!", "email": rated_user.email}

    return {"message": "User has been rated.","email": None}


async def add_rating(rater_id: int, rated_user: UserModel, session):
    """Добавляет оценку пользователя, если он еще не был оценён."""

    if await check_existing_rating(rater_id, rated_user.id, session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user has already been rated.",
        )

    await save_new_rating(rater_id, rated_user.id, session)


async def check_existing_rating(rater_id: int, rated_id: int, session) -> bool:
    """Проверяет, существует ли оценка для данного пользователя."""
    query = select(Rating).where(
        Rating.rater_id == rater_id, Rating.rated_id == rated_id
    )
    result = await session.execute(query)
    return result.scalars().first() is not None


async def save_new_rating(rater_id: int, rated_id: int, session):
    """Сохраняет новую запись оценки."""
    new_rating = Rating(rater_id=rater_id, rated_id=rated_id)
    session.add(new_rating)
    await session.commit()


async def get_all_users(user: UserModel, filters: UserFilter, session) -> list:
    """Получает список пользователей с применением фильтров и сортировки."""
    query = select(UserModel)
    query = await apply_filters_and_sorting(filters, query)
    query = query.filter(UserModel.id != user.id)

    result = await session.execute(query)
    users = result.scalars().all()

    if filters.max_distance:
        users = calculate_distance(user, users, filters.max_distance)

    return users


async def apply_filters_and_sorting(filters: UserFilter, query):
    """Применяет фильтры и сортировку к запросу."""
    query = apply_filters(filters, query)
    query = apply_sorting(filters, query)
    return query


def apply_filters(filters: UserFilter, query):
    """Применяет фильтры на основе данных атрибутов фильтрации пользователя."""
    if filters.gender:
        query = query.filter(UserModel.gender == filters.gender)
    if filters.first_name:
        query = query.filter(UserModel.first_name.ilike(f"%{filters.first_name}%"))
    if filters.last_name:
        query = query.filter(UserModel.last_name.ilike(f"%{filters.last_name}%"))
    return query


def apply_sorting(filters: UserFilter, query):
    """Применяет сортировку по дате регистрации."""
    if filters.sort_by_registration == SORT_BY_RECENT:
        query = query.order_by(asc(UserModel.created_at))
    elif filters.sort_by_registration == SORT_BY_OLDEST:
        query = query.order_by(desc(UserModel.created_at))
    return query
