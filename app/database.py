import asyncio

import config as con
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from models import Base
data_base_url = f'postgresql+asyncpg://{con.DB_USER}:{con.DB_PASS}@{con.DB_HOST}/{con.DB_NAME}'

engine = create_async_engine(data_base_url, echo=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, excepire_on_commit=False
)

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init_models())