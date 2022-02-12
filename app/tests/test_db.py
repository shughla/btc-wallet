import sqlite3
from sqlite3 import Connection

from app.core.models.user import User
from app.core.models.wallet import DefaultWallet
from app.core.repositories import IWalletRepository
from app.core.security.api_key_generator import ApiKey
from app.infra.repositories.inmemory.user import InMemoryUserRepository
from app.infra.repositories.inmemory.wallet import InMemoryWalletRepository
from app.infra.repositories.sqlite.user import SQLiteUserRepository
from app.infra.repositories.sqlite.wallet import SQLiteWalletRepository


def get_connection() -> Connection:
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


def test_repository(
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
    test_repository(SQLiteWalletRepository(get_connection()))
