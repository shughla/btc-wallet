import sqlite3
from sqlite3 import Connection
from typing import Protocol

from fastapi import FastAPI

from app.core.facade import Facade
from app.core.interceptors.user import UserInterceptor
from app.core.interceptors.wallet import WalletInterceptor
from app.core.security.api_key_generator import ApiKeyGenerator
from app.infra.fastapi.api import api_router
from app.infra.repositories.inmemory.user import InMemoryUserRepository
from app.infra.repositories.inmemory.wallet import InMemoryWalletRepository
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
        app.state.facade = Facade(
            UserInterceptor(SQLiteUserRepository(connection)),
            WalletInterceptor(SQLiteWalletRepository(connection)),
        )
        app.include_router(api_router)
        return app


class TestAppFactory(AppFactory):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        app.state.facade = Facade(
            UserInterceptor(InMemoryUserRepository(), ApiKeyGenerator()),
            WalletInterceptor(InMemoryWalletRepository()),
        )
        app.include_router(api_router)
        return app
