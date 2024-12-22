from fastapi import FastAPI
from app.database import init_db
from app.api import api_router

app = FastAPI()


app.include_router(api_router)


@app.on_event("startup")
async def startup():
    await init_db()
