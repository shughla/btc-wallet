from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions import (
    NotEnoughMoneyException,
    WalletNotFoundException,
    WrongWalletRequestException,
)
from app.core.facade import IFacade
from app.core.models.transaction import Transaction
from app.core.models.user import User
from app.core.schemas.transaction import TransactionRequest, TransactionResponse
from app.infra.fastapi.deps import get_authenticated_user, get_facade

router = APIRouter()


@router.post("/transaction", status_code=HTTPStatus.CREATED)
def create_transaction(
    request: TransactionRequest,
    facade: IFacade = Depends(get_facade),
    user: User = Depends(get_authenticated_user),
) -> int:
    try:
        return facade.create_transaction(user, request)
    except (
        NotEnoughMoneyException,
        WrongWalletRequestException,
        WalletNotFoundException,
    ) as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=str(e))


@router.get(
    "/transaction", status_code=HTTPStatus.OK, response_model=list[TransactionResponse]
)
def get_transactions(
    facade: IFacade = Depends(get_facade), _: User = Depends(get_authenticated_user)
) -> list[Transaction]:
    transactions = facade.get_all_transactions()
    return transactions
