import sqlite3
from sqlite3 import Connection
from typing import Protocol

from fastapi import FastAPI

from app.core.facade import Facade, StatisticsInterceptor
from app.core.interceptors.rate_converter import DummySatoshiRateConverter
from app.core.interceptors.transaction import (
    InMemoryStatisticsRepository,
    SQLiteStatisticsRepository,
    TransactionCalculator,
    TransactionInterceptor,
)
from app.core.interceptors.user import UserInterceptor
from app.core.interceptors.wallet import WalletInterceptor
from app.core.security.api_key_generator import ApiKeyGenerator
from app.infra.fastapi.api import api_router
from app.infra.repositories.inmemory.transaction import InMemoryTransactionRepository
from app.infra.repositories.inmemory.user import InMemoryUserRepository
from app.infra.repositories.inmemory.wallet import InMemoryWalletRepository
from app.infra.repositories.sqlite.transaction import SQLiteTransactionRepository
from app.infra.repositories.sqlite.user import SQLiteUserRepository
from app.infra.repositories.sqlite.wallet import SQLiteWalletRepository


class AppFactory(Protocol):
    def create_app(self) -> FastAPI:
        pass


def get_db_connection() -> Connection:
    return sqlite3.connect("sqlite_db", check_same_thread=False)


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


TEST_COMMISSION_PERCENT = 0.5


class TestAppFactory(AppFactory):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        wallet_repository = InMemoryWalletRepository()
        app.state.facade = Facade(
            UserInterceptor(InMemoryUserRepository(), ApiKeyGenerator()),
            WalletInterceptor(wallet_repository),
            TransactionInterceptor(
                InMemoryTransactionRepository(),
                wallet_repository,
                TransactionCalculator(TEST_COMMISSION_PERCENT),
            ),
            StatisticsInterceptor(InMemoryStatisticsRepository()),
            DummySatoshiRateConverter(),
        )
        app.include_router(api_router)
        return app
