import os
from dotenv import load_dotenv
from crypto_utils import load_private_key, load_public_key


load_dotenv()

# Настройки аутентификации и JWT
algorithm = os.getenv("algorithm")
access_token_expire = os.getenv("access_token_expire")

# Настройки базы данных
DB_HOST = os.getenv("HOST")
DB_USER = os.getenv("USER")
DB_PASS = os.getenv("PASSWORD")
DB_NAME = os.getenv("DATABASE")
DB_PORT = os.getenv("PORT")
data_base_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Пути для работы с изображениями
AVATAR_DIR = "photo/avatar"
WATERMARK_DIR = "photo/watermark/photo_2024-10-31_16-57-13.jpg"

# Другие настройки
daily_rating_limit = 5
email_password = os.getenv("email_password")
base_email = os.getenv("email")
host_email = os.getenv('host_email')
port_email = os.getenv('port_email')

# Пути к публичному и приватному ключам из переменных окружения
public_path = os.getenv("public_path")
private_path = os.getenv("private_path")


private_key = load_private_key(private_path)
public_key = load_public_key(public_path)
