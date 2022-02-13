import pytest

from app.core.calculator import TransactionCalculator
from app.core.exceptions import (
    MaximumWalletAmountReachedException,
    NotEnoughMoneyException,
)
from app.core.interceptors.wallet import WalletInterceptor
from app.core.models.currency import CurrencyRate
from app.core.models.user import User
from app.core.models.wallet import DefaultWallet, Wallet
from app.core.schemas.wallet import WalletResponseBuilder
from app.core.security.api_key_generator import ApiKey, ApiKeyGenerator
from app.infra.repositories.inmemory.wallet import InMemoryWalletRepository


def test_wallet_interceptor() -> None:
    user = User(0, ApiKey("asd"))
    max_wallets = 5
    interceptor = WalletInterceptor(InMemoryWalletRepository(), max_wallets)
    for i in range(8):
        if i < max_wallets:
            interceptor.create_wallet(user)
        else:
            try:
                interceptor.create_wallet(user)
                assert False
            except MaximumWalletAmountReachedException:
                pass


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


def test_default_generator() -> None:
    keys = set()
    generator = ApiKeyGenerator()
    for i in range(10000):
        key = generator.generate_api_key()
        assert key not in keys
        keys.add(key)
