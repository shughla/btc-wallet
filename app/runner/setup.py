from abc import ABC, abstractmethod

from fastapi import FastAPI

from app.core.calculator import TransactionCalculator
from app.core.facade import Facade
from app.core.interactors.statistics import StatisticsInteractor
from app.core.interactors.transaction import TransactionInteractor
from app.core.interactors.user import UserInteractor
from app.core.interactors.wallet import WalletInteractor
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


class AppFactory(ABC):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        app = self.change_app(app)
        app.include_router(api_router)
        return app

    @abstractmethod
    def change_app(self, app: FastAPI) -> FastAPI:
        pass


class DevelopmentAppFactory(AppFactory):
    def change_app(self, app: FastAPI) -> FastAPI:
        connection = get_connection()
        wallet_repository = SQLiteWalletRepository(connection)
        user_interactor = UserInteractor(SQLiteUserRepository(connection))
        wallet_interactor = WalletInteractor(wallet_repository)
        transaction_interactor = TransactionInteractor(
            SQLiteTransactionRepository(connection), wallet_repository
        )
        stats_interactor = StatisticsInteractor(SQLiteStatisticsRepository(connection))
        app.state.facade = Facade(
            user_interactor, wallet_interactor, transaction_interactor, stats_interactor
        )
        return app


TEST_COMMISSION_PERCENT = 0.5


class TestAppFactory(AppFactory):
    def change_app(self, app: FastAPI) -> FastAPI:
        wallet_repository = InMemoryWalletRepository()
        user_interactor = UserInteractor(InMemoryUserRepository(), ApiKeyGenerator())
        wallet_interactor = WalletInteractor(wallet_repository)
        transaction_interactor = TransactionInteractor(
            InMemoryTransactionRepository(),
            wallet_repository,
            TransactionCalculator(TEST_COMMISSION_PERCENT),
        )
        stats_interactor = StatisticsInteractor(InMemoryStatisticsRepository())
        converter = DummySatoshiRateConverter()
        app.state.facade = Facade(
            user_interactor,
            wallet_interactor,
            transaction_interactor,
            stats_interactor,
            converter,
        )
        return app
