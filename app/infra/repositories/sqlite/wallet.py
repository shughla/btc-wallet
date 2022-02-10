from sqlite3 import Connection

from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.repositories import IWalletRepository


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
        print("cursor executed, inserted")
        wallet.address = cursor.lastrowid
        cursor.close()
        return wallet
