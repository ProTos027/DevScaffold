from fastapi import APIRouter
from app.api.v1.endpoints import users, gamesnnapi_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(games.router)