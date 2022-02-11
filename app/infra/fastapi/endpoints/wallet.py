from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.core.exceptions import WrongWalletRequestException
from app.core.facade import IFacade
from app.core.interceptors.rate_converter import Currency, CurrencyRate
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.schemas.wallet import WalletResponse, WalletResponseBuilder
from app.infra.fastapi.deps import get_authenticated_user, get_facade

router = APIRouter()


@router.post("/wallet", status_code=HTTPStatus.CREATED)  # type: ignore
def create_wallet(
    facade: IFacade = Depends(get_facade), user: User = Depends(get_authenticated_user)
) -> WalletResponse:
    wallet = facade.create_wallet(user)
    if wallet is None:
        raise HTTPException(HTTPStatus.BAD_REQUEST)
    return get_wallet_response(facade, wallet)


@router.get("/wallet/{address}", status_code=HTTPStatus.OK)  # type: ignore
def get_wallet(
    address: int,
    facade: IFacade = Depends(get_facade),
    user: User = Depends(get_authenticated_user),
) -> WalletResponse:
    try:
        wallet = facade.get_wallet(user, address)
        return get_wallet_response(facade, wallet)
    except WrongWalletRequestException:
        raise HTTPException(HTTPStatus.BAD_REQUEST)


def get_wallet_response(facade: IFacade, wallet: Wallet) -> WalletResponse:
    satoshis_to_btc = facade.get_satoshi_rate(Currency.BTC)
    satoshis_to_usd = facade.get_satoshi_rate(Currency.USD)
    return (
        WalletResponseBuilder(wallet)
        .with_currency(CurrencyRate(Currency.USD, satoshis_to_usd))
        .with_currency(CurrencyRate(Currency.BTC, satoshis_to_btc))
        .create()
    )
