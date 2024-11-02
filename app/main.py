from fastapi import FastAPI

from .routers.users_router import users_router


app = FastAPI(title='User')
app.include_router(users_router)