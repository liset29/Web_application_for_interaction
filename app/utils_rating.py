import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from app.models import Rating
from config import daily_rating_limit, email_password, base_email
from sqlalchemy import select, func


async def check_daily_limit(user_id: int, db):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    stmt = select(func.count()).select_from(Rating).where(
        Rating.rater_id == user_id,
        Rating.created_at >= today_start,
        Rating.created_at < today_end
    )

    result = await db.execute(stmt)
    daily_ratings_count = result.scalar()

    return daily_ratings_count < daily_rating_limit


async def send_email(users_info: list):
    sender = base_email
    password = email_password
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(sender, password)

        for user_info in users_info:
            email = user_info["email_rater"]
            username = user_info["username_rated"]
            email_rated = user_info["email_rated"]

            message = f"Вы понравились {username}! Почта участника: {email_rated}"
            msg = MIMEText(message)
            msg['Subject'] = 'Mutual sympathy'

            try:
                server.sendmail(sender, email, msg.as_string())
                print(f"Сообщение успешно отправлено на {email}")
            except Exception as ex:
                print(f"Ошибка при отправке на {email}: {ex}")

    finally:
        server.quit()



