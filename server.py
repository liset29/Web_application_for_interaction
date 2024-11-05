import asyncio

import uvicorn

from app.database import init_models

async def start_app():
    await init_models()
    config = uvicorn.Config("app.main:app", host="0.0.0.0", port=80, reload=True)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_app())