from sqlite3 import Connection
from typing import Protocol

from fastapi import FastAPI

from app.core.const import Config
from app.core.facade import Facade
from app.core.interceptors.statistics import StatisticsInterceptor
from app.core.interceptors.transaction import TransactionInterceptor
from app.core.interceptors.user import UserInterceptor
from app.core.interceptors.wallet import WalletInterceptor
from app.infra.fastapi.api import api_router
from app.infra.repositories.sqlite.statistics import SQLiteStatisticsRepository
from app.infra.repositories.sqlite.transaction import SQLiteTransactionRepository
from app.infra.repositories.sqlite.user import SQLiteUserRepository
from app.infra.repositories.sqlite.utils import get_connection
from app.infra.repositories.sqlite.wallet import SQLiteWalletRepository


class AppFactory(Protocol):
    def create_app(self) -> FastAPI:
        pass


def get_db_connection() -> Connection:
    with get_connection(Config.DATABASE_NAME) as conn:
        return conn


class DevelopmentAppFactory(AppFactory):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        connection = get_db_connection()
        wallet_repository = SQLiteWalletRepository(connection)
        app.state.facade = Facade(
            UserInterceptor(SQLiteUserRepository(connection)),
            WalletInterceptor(wallet_repository),
            TransactionInterceptor(
                SQLiteTransactionRepository(connection),
                wallet_repository,
            ),
            StatisticsInterceptor(SQLiteStatisticsRepository(connection)),
        )
        app.include_router(api_router)
        return app
