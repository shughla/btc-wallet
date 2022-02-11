from sqlite3 import Connection

from app.core.exceptions import WrongWalletRequestException
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.repositories import IWalletRepository
from app.infra.repositories.sqlite import get_cursor


class SQLiteWalletRepository(IWalletRepository):
    connection: Connection

    def __init__(self, connection: Connection) -> None:

        self.connection = connection
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "create table if not exists wallet("
                "wallet_id integer primary key autoincrement,"
                "balance_satoshi integer not null,"
                "user_id integer references user(user_id));"
            )

    def get_wallets(self, user: User) -> list[Wallet]:
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "select wallet_id, user_id, balance_satoshi from wallet "
                "where user_id = :user_id",
                {"user_id": user.id},
            )
            wallets = cursor.fetchall()
            return list(
                map(
                    lambda row: Wallet(address=row[0], user_id=row[1], balance=row[2]),
                    wallets,
                )
            )

    def get_wallet(self, address: int) -> Wallet:
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "select wallet_id, user_id, balance_satoshi from wallet "
                "where wallet_id = :address",
                {"address": address},
            )
            wallet = cursor.fetchone()
            if len(wallet) == 0:
                raise WrongWalletRequestException()
            return Wallet(address=wallet[0], user_id=wallet[1], balance=wallet[2])

    def add_wallet(self, wallet: Wallet) -> Wallet:
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "insert into wallet(user_id, balance_satoshi) " "values(:id, :balance)",
                {"id": wallet.user_id, "balance": wallet.balance},
            )
            wallet.address = cursor.lastrowid
            return wallet
