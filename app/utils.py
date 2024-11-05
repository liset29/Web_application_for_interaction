import math
import smtplib

from email.mime.text import MIMEText
from datetime import datetime, timedelta
from geopy.distance import great_circle
from loguru import logger

from app.models import Rating, UserModel
from config import daily_rating_limit, email_password, base_email, host_email, port_email
from sqlalchemy import select, func

from const import MUTUAL_SYMPATHY_SUBJECT


async def check_daily_limit(user_id: int, db) -> bool:
    '''Проверяет количество оценок пользователя'''
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    stmt = (
        select(func.count())
        .select_from(Rating)
        .where(
            Rating.rater_id == user_id,
            Rating.created_at >= today_start,
            Rating.created_at < today_end,
        )
    )

    result = await db.execute(stmt)
    daily_ratings_count = result.scalar()

    return daily_ratings_count < daily_rating_limit



async def send_email(users_info: list) -> None:
    '''Отправляет email-сообщение пользователям при взаимной симпатии.'''
    server = smtplib.SMTP(host_email, port_email)
    server.starttls()

    try:
        login_to_email_server(server)
        for user_info in users_info:
            email = user_info.get("email_rater")
            username = user_info.get("username_rated")
            email_rated = user_info.get("email_rated")
            message = create_email_message(username, email_rated)

            send_message(server, email, message)
    finally:
        server.quit()


def login_to_email_server(server: smtplib.SMTP) -> None:
    '''Авторизуется на email сервере.'''
    try:
        server.login(base_email, email_password)
    except Exception as ex:
        logger.error(f"Ошибка входа на сервер: {ex}")
        raise


def create_email_message(username: str, email_rated: str) -> MIMEText:
    '''Создает сообщение с уведомлением о взаимной симпатии.'''
    message_content = f"Вы понравились {username}! Почта участника: {email_rated}"
    message = MIMEText(message_content)
    message["Subject"] = MUTUAL_SYMPATHY_SUBJECT
    return message


def send_message(server: smtplib.SMTP, recipient_email: str, message: MIMEText) -> None:
    '''Отправляет email на указанный адрес.'''
    try:
        server.sendmail(base_email, recipient_email, message.as_string())
    except Exception as ex:
        logger.error(f"Ошибка отправки сообщения на {recipient_email}: {ex}")



def calculate_distance(user: UserModel, users: list, max_distance: float) -> list:
    '''Рассчитывает дистанцию между пользователями '''
    result = []
    coord1 = (user.latitude, user.longitude)
    for i in users:
        coord2 = (i.latitude, i.longitude)
        distance = great_circle(coord1, coord2).kilometers
        if distance <= max_distance:
            result.append(i)

    return result
