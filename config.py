import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()

algorithm = os.getenv('algorithm')
access_token_expire = os.getenv('access_token_expire')

DB_HOST = os.getenv('HOST')
DB_USER = os.getenv('USER')
DB_PASS = os.getenv('PASSWORD')
DB_NAME = os.getenv('DATABASE')
DB_PORT = os.getenv('PORT')
public_path = os.getenv('public_path')
private_path = os.getenv('private_path')
data_base_url = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}'
AVATAR_DIR = "photo/avatar"
WATERMARK_DIR = "photo/watermark/photo_2024-10-31_16-57-13.jpg"
def load_private_key():
    with open(f"{private_path}", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key


def load_public_key():
    with open(f"{public_path}", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return public_key


private_key = load_private_key()
public_key = load_public_key()

