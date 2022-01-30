from fastapi import FastAPI

from app.infra.fastapi.api.api import api_router


def setup() -> FastAPI:
    app = FastAPI(reload=True)

    app.include_router(api_router)

    return app
