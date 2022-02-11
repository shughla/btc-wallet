import sqlite3
from http import HTTPStatus
from typing import Any

from starlette.testclient import TestClient

from app.core.interceptors.rate_converter import CurrencyRate
from app.core.interceptors.wallet import WalletInterceptor
from app.core.models.user import User
from app.core.models.wallet import DefaultWallet, Wallet
from app.core.repositories import IWalletRepository
from app.core.schemas.wallet import WalletResponseBuilder
from app.core.security.api_key_generator import ApiKey
from app.infra.repositories.inmemory.user import InMemoryUserRepository
from app.infra.repositories.inmemory.wallet import InMemoryWalletRepository
from app.infra.repositories.sqlite.user import SQLiteUserRepository
from app.infra.repositories.sqlite.wallet import SQLiteWalletRepository
from app.runner.setup import TestAppFactory

appFactory = TestAppFactory()
app = appFactory.create_app()
client = TestClient(app)


def test_get_items() -> None:
    response = client.post("/user")
    assert response.status_code == HTTPStatus.CREATED
    assert (
        len(response.json()["api_key"]) >= 16
    )  # key should be at least 16 symbols for randomness


def get_connection() -> Any:
    return sqlite3.connect(":memory:", check_same_thread=False)


def test_same_api_key() -> None:
    repo = InMemoryUserRepository()
    key = ApiKey("asdasdasd")
    not_added_key = ApiKey("asd")
    repo.add_user(key)
    assert repo.find(key) is not None
    assert repo.find(not_added_key) is None


def test_sqlite_user_repository() -> None:
    repo = SQLiteUserRepository(get_connection())
    key = ApiKey("test")
    repo.add_user(key)
    assert repo.find(key) is not None


def test_inmemory_repository(
    repo: IWalletRepository = InMemoryWalletRepository(),
) -> None:
    user = User(0, ApiKey("key"))
    assert len(repo.get_wallets(user)) == 0
    wallet = DefaultWallet(0)
    repo.add_wallet(wallet)
    assert len(repo.get_wallets(user)) == 1
    repo.add_wallet(DefaultWallet(0))
    repo.add_wallet(DefaultWallet(0))
    assert len(repo.get_wallets(user)) == 3


def test_sqlite_wallet_repository() -> None:
    test_inmemory_repository(SQLiteWalletRepository(get_connection()))


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
    assert wallet_response.amounts[0].currency == "USD"
    assert wallet_response.amounts[0].balance == 10
    assert wallet_response.amounts[1].currency == "EUR"
    assert wallet_response.amounts[1].balance == 12
    assert wallet_response.amounts[2].currency == "GBP"
    assert wallet_response.amounts[2].balance == 15
    assert wallet_response.amounts[3].currency == "BTC"
    assert wallet_response.amounts[3].balance == 0.001
