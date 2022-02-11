from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions import (
    DuplicateUserApiKeyException,
    NotEnoughMoneyException,
    WrongWalletRequestException,
)
from app.core.facade import IFacade
from app.core.models.user import User
from app.core.schemas.transaction import TransactionRequest
from app.infra.fastapi.deps import get_authenticated_user, get_facade

router = APIRouter()


@router.post("/transaction", status_code=HTTPStatus.CREATED)  # type: ignore
def create_transaction(
    request: TransactionRequest,
    facade: IFacade = Depends(get_facade),
    user: User = Depends(get_authenticated_user),
) -> int:
    try:
        return facade.create_transaction(user, request)
    except NotEnoughMoneyException:
        raise HTTPException(HTTPStatus.BAD_REQUEST)
    except WrongWalletRequestException:
        raise HTTPException(HTTPStatus.BAD_REQUEST)
