from http import HTTPStatus

from fastapi import APIRouter, Depends

from app.core.facade import IFacade
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.schemas.wallet import WalletResponse
from app.infra.fastapi.deps import get_authenticated_user, get_facade

router = APIRouter()


@router.post("/wallet", status_code=HTTPStatus.CREATED, response_model=WalletResponse)  # type: ignore
def create_wallet(
    facade: IFacade = Depends(get_facade), user: User = Depends(get_authenticated_user)
) -> Wallet:
    return facade.create_wallet(user)
