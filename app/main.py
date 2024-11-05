from fastapi import FastAPI


from .routers.users_router import users_router


app = FastAPI(title="Timurs Dating App")
app.include_router(users_router)
