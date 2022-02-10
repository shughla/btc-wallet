from dataclasses import dataclass, field
from sqlite3 import Connection
from typing import Optional, Protocol

from app.core.interceptors.user import IUserInterceptor
from app.core.interceptors.wallet import IWalletInterceptor
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.repositories import IWalletRepository
from app.core.security.api_key_generator import ApiKey


class IFacade(Protocol):
    def create_user(self) -> ApiKey:
        pass

    def create_wallet(self, user: User) -> Wallet:
        pass

    def authenticate(self, api_key: ApiKey) -> Optional[User]:
        pass


@dataclass
class InMemoryWalletRepository(IWalletRepository):
    wallets: dict[int, list[Wallet]] = field(default_factory=dict)
    last_wallet: int = 0

    def get_wallets(self, user: User) -> list[Wallet]:
        return self.wallets.get(user.id, [])

    def add_wallet(self, wallet: Wallet) -> Wallet:
        wallet.address = self.last_wallet
        if self.wallets.get(wallet.user_id) is None:
            self.wallets[wallet.user_id] = [wallet]
        else:
            self.wallets[wallet.user_id].append(wallet)
        self.last_wallet += 1
        return wallet


class SQLiteWalletRepository(IWalletRepository):
    connection: Connection

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute(
            "create table if not exists wallet("
            "wallet_id integer primary key autoincrement,"
            "balance_satoshi integer not null,"
            "user_id integer references user(user_id));"
        )
        cursor.close()

    def get_wallets(self, user: User) -> list[Wallet]:
        cursor = self.connection.cursor()
        cursor.execute(
            "select wallet_id, user_id, balance_satoshi from wallet "
            "where user_id = :user_id",
            {"user_id": user.id},
        )
        wallets = cursor.fetchall()
        cursor.close()
        return list(
            map(
                lambda row: Wallet(address=row[0], user_id=row[1], balance=row[2]),
                wallets,
            )
        )

    def add_wallet(self, wallet: Wallet) -> Wallet:
        cursor = self.connection.cursor()
        cursor.execute(
            "insert into wallet(user_id, balance_satoshi) " "values(:id, :balance)",
            {"id": wallet.user_id, "balance": wallet.balance},
        )
        wallet.address = cursor.lastrowid
        cursor.close()
        return wallet


@dataclass
class Facade(IFacade):
    user_interceptor: IUserInterceptor
    wallet_interceptor: IWalletInterceptor

    def create_user(self) -> ApiKey:
        return self.user_interceptor.create_user()

    def create_wallet(self, user: User) -> Wallet:
        return self.wallet_interceptor.create_wallet(user)

    def authenticate(self, api_key: ApiKey) -> Optional[User]:
        return self.user_interceptor.get_user(api_key)
