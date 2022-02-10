from fastapi import APIRouter

from app.infra.fastapi.endpoints import user, wallet

api_router = APIRouter()
api_router.include_router(user.router)
api_router.include_router(wallet.router)
