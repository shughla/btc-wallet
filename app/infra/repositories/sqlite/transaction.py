from sqlite3 import Connection

from app.core.models.transaction import Transaction
from app.core.repositories import ITransactionRepository
from app.infra.repositories.sqlite import get_cursor


class SQLiteTransactionRepository(ITransactionRepository):
    connection: Connection

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "create table if not exists transactions("
                "transaction_id integer primary key autoincrement,"
                "from_wallet integer not null,"
                "to_wallet integer not null,"
                "amount integer not null,"
                "commission integer not null);"
            )

    def add_transaction(self, request: Transaction) -> None:
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "insert into transactions(from_wallet, to_wallet, amount, commission) "
                "values(:from_wallet, :to_wallet, :amount, :commission);",
                {
                    "from_wallet": request.from_wallet,
                    "to_wallet": request.to_wallet,
                    "amount": request.amount,
                    "commission": request.commission,
                },
            )