import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('HOST')
DB_USER = os.getenv('USER')
DB_PASS = os.getenv('PASSWORD')
DB_NAME = os.getenv('DATABASE')
DB_PORT = os.getenv('PORT')
