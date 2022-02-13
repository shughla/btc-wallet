from dataclasses import dataclass
from sqlite3 import Connection

from app.core.models.statistics import Statistics
from app.core.repositories import IStatisticsRepository
from app.infra.repositories.sqlite.utils import get_cursor


@dataclass
class SQLiteStatisticsRepository(IStatisticsRepository):
    connection: Connection

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "create table if not exists statistics("
                "id integer primary key check (id = 0),"
                "total_transactions integer not null default 0,"
                "profit integer not null default 0);"
            )
            cursor.execute("select * from statistics where id = 0")
            if cursor.fetchone() is None:
                cursor.execute("insert into statistics(id) values(0)")

    def record_transaction(self, commission: int) -> None:
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "update statistics SET "
                "total_transactions = statistics.total_transactions + 1, "
                "profit = profit + :commission WHERE id = 0",
                {"commission": commission},
            )

    def get_statistics(self) -> Statistics:
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "select total_transactions, profit from statistics where id = 0"
            )
            res = cursor.fetchone()
            return Statistics(res[0], res[1])
