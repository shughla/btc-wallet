import pytest

from app.core.exceptions import NotEnoughMoneyException
from app.core.interceptors.rate_converter import CurrencyRate
from app.core.interceptors.transaction import TransactionCalculator
from app.core.interceptors.wallet import WalletInterceptor
from app.core.models.user import User
from app.core.models.wallet import DefaultWallet, Wallet
from app.core.schemas.wallet import WalletResponseBuilder
from app.core.security.api_key_generator import ApiKey
from app.infra.repositories.inmemory.wallet import InMemoryWalletRepository


def test_wallet_interceptor() -> None:
    user = User(0, ApiKey("asd"))
    interceptor = WalletInterceptor(wallet_repository=InMemoryWalletRepository())
    for i in range(8):
        wallet = interceptor.create_wallet(user)
        if i < 3:
            assert wallet is not None
        else:
            assert wallet is None


def test_wallet_response_creator() -> None:
    wallet = Wallet(address=1, user_id=-1, balance=10)
    currencies = [
        CurrencyRate(currency="USD", rate=1),
        CurrencyRate(currency="EUR", rate=1.2),
        CurrencyRate(currency="GBP", rate=1.5),
        CurrencyRate(currency="BTC", rate=0.0001),
    ]

    wallet_response = (
        WalletResponseBuilder(wallet=wallet)
        .with_currency(currencies[0])
        .with_currency(currencies[1])
        .with_currency(currencies[2])
        .with_currency(currencies[3])
        .create()
    )

    assert wallet_response.address == 1
    assert wallet_response.balance_currencies[0].currency == "USD"
    assert wallet_response.balance_currencies[0].balance == 10
    assert wallet_response.balance_currencies[1].currency == "EUR"
    assert wallet_response.balance_currencies[1].balance == 12
    assert wallet_response.balance_currencies[2].currency == "GBP"
    assert wallet_response.balance_currencies[2].balance == 15
    assert wallet_response.balance_currencies[3].currency == "BTC"
    assert wallet_response.balance_currencies[3].balance == 0.001


def test_transaction_commission() -> None:
    wallet1 = DefaultWallet(0)
    wallet2 = DefaultWallet(1)
    wallet3 = DefaultWallet(0)
    calculator = TransactionCalculator(0.5)
    assert 500 == calculator.get_balances(1000, wallet1, wallet2)
    assert 0 == calculator.get_balances(500, wallet1, wallet3)
    with pytest.raises(NotEnoughMoneyException):
        assert calculator.get_balances(10**15, wallet1, wallet1)
        assert calculator.get_balances(10**15, wallet1, wallet2)
        assert calculator.get_balances(10**15, wallet1, wallet3)
