from http import HTTPStatus
from typing import Any

from fastapi import Depends, Header, HTTPException
from starlette.requests import Request

from app.core.const import Config
from app.core.facade import IFacade
from app.core.models.user import User
from app.core.security.api_key_generator import ApiKey


def get_facade(request: Request) -> Any:
    return request.app.state.facade


def can_access_admin(authorization: str = Header(None)) -> bool:
    if authorization == Config.ADMIN_KEY:
        return True
    return False


def get_authenticated_user(
    facade: IFacade = Depends(get_facade), authorization: str = Header(None)
) -> User:
    user = facade.authenticate(ApiKey(authorization))
    if user is None:
        raise HTTPException(HTTPStatus.UNAUTHORIZED)
    else:
        return user
