import asyncio
from app.db_helper import db_helper
from .models import Base


async def init_models():
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


