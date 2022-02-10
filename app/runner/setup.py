from typing import Protocol

from fastapi import FastAPI

from app.infra.fastapi.api import api_router


class AppFactory(Protocol):
    def create_app(self) -> FastAPI:
        pass


class DevelopmentAppFactory(AppFactory):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(api_router)
        return app


class TestAppFactory(AppFactory):
    def create_app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(api_router)
        return app
