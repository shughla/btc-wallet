from typing import Any

from starlette.requests import Request


def get_facade(request: Request) -> Any:
    return request.app.state.facade
