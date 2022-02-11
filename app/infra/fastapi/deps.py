from http import HTTPStatus
from typing import Any

from fastapi import Depends, Header, HTTPException
from starlette.requests import Request

from app.core.facade import IFacade
from app.core.models.user import User
from app.core.security.api_key_generator import ApiKey


def get_facade(request: Request) -> Any:
    return request.app.state.facade


def get_authenticated_user(
    facade: IFacade = Depends(get_facade), api_key: str = Header(None)
) -> User:
    user = facade.authenticate(ApiKey(api_key))
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)
    else:
        return user
