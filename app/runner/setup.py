from typing import Protocol

from fastapi import FastAPI

from app.core.calculator import TransactionCalculator
from app.core.facade import Facade
from app.core.interceptors.statistics import StatisticsInterceptor
from app.core.interceptors.transaction import TransactionInterceptor
from app.core.interceptors.user import UserInterceptor
from app.core.interceptors.wallet import WalletInterceptor
from app.core.security.api_key_generator import ApiKeyGenerator
from app.infra.fastapi.api import api_router
from app.infra.repositories.inmemory.statistics import InMemoryStatisticsRepository
from app.infra.repositories.inmemory.transaction import InMemoryTransactionRepository
from app.infra.repositories.inmemory.user import InMemoryUserRepository
from app.infra.repositories.inmemory.wallet import InMemoryWalletRepository
from app.infra.repositories.sqlite.statistics import SQLiteStatisticsRepository
from app.infra.repositories.sqlite.transaction import SQLiteTransactionRepository
from app.infra.repositories.sqlite.user import SQLiteUserRepository
from app.infra.repositories.sqlite.utils import get_connection
from app.infra.repositories.sqlite.wallet import SQLiteWalletRepository
from app.tests.dummies import DummySatoshiRateConverter


class AppFactory(Protocol):
    def create_app(self) -> FastAPI:
        pass


class DevelopmentAppFactory(AppFactory):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        connection = get_connection()
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
