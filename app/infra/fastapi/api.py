from fastapi import APIRouter

from app.infra.fastapi.endpoints import statistics, transaction, user, wallet

api_router = APIRouter()
api_router.include_router(user.router, tags=["User"])
api_router.include_router(wallet.router, tags=["Wallet"])
api_router.include_router(transaction.router, tags=["Transaction"])
api_router.include_router(statistics.router, tags=["Statistics"])
