from fastapi import APIRouter

from app.infra.fastapi.endpoints import user

api_router = APIRouter()
api_router.include_router(user.router)
