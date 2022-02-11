from dataclasses import dataclass
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.core.facade import IFacade
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.schemas.wallet import WalletResponse
from app.infra.fastapi.deps import get_authenticated_user, get_facade

router = APIRouter()

# TODO: this is temporary to test api, change later


@dataclass
class WalletWithRates:
    address: int
    balance_usd: float
    balance_bitcoin: float

    def __init__(self, wallet: Wallet, usd_rate: float) -> None:
        self.address = wallet.address
        self.balance_usd = wallet.balance * usd_rate
        self.balance_bitcoin = wallet.balance / 100_000_000


@router.post("/wallet", status_code=HTTPStatus.CREATED, response_model=WalletResponse)  # type: ignore
def create_wallet(
    facade: IFacade = Depends(get_facade), user: User = Depends(get_authenticated_user)
) -> WalletWithRates:
    wallet = facade.create_wallet(user)
    if wallet is None:
        raise HTTPException(HTTPStatus.BAD_REQUEST)
    # TODO: after this is temporary
    rate = 0.000000052
    wallet_with_rates = WalletWithRates(wallet, rate)
    return wallet_with_rates
