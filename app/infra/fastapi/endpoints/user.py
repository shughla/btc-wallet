from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions import DuplicateUserApiKeyException
from app.core.facade import IFacade
from app.core.security.api_key_generator import ApiKey
from app.infra.fastapi.deps import get_facade

router = APIRouter()


@router.post("/user", status_code=HTTPStatus.CREATED)
def create_user(facade: IFacade = Depends(get_facade)) -> ApiKey:
    try:
        return facade.create_user()
    except DuplicateUserApiKeyException:
        raise HTTPException(HTTPStatus.BAD_REQUEST)
