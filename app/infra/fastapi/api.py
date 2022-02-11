from fastapi import APIRouter

from app.infra.fastapi.endpoints import transaction, user, wallet

api_router = APIRouter()
api_router.include_router(user.router, tags=["user"])
api_router.include_router(wallet.router, tags=["wallet"])
api_router.include_router(transaction.router, tags=["transaction"])
