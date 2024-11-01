from fastapi import FastAPI

from .routers.auth_router import auth_router


app = FastAPI(title='User')
app.include_router(auth_router)