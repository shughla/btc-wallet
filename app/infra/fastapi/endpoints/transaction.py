from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions import NotEnoughMoneyException, WrongWalletRequestException
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
    except NotEnoughMoneyException:
        raise HTTPException(HTTPStatus.BAD_REQUEST)
    except WrongWalletRequestException:
        raise HTTPException(HTTPStatus.BAD_REQUEST)


@router.get(
    "/transaction",
    status_code=HTTPStatus.OK,
    response_model=list[TransactionResponse],
    response_model_exclude_unset=True,
)
def get_transactions(
    facade: IFacade = Depends(get_facade), user: User = Depends(get_authenticated_user)
) -> list[Transaction]:
    transaction = facade.get_all_transaction(user)
    return transaction
