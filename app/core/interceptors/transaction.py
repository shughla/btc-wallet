from dataclasses import dataclass, field
from sqlite3 import Connection
from typing import Protocol

from app.core.exceptions import NotEnoughMoneyException, WrongWalletRequestException
from app.core.models.statistics import Statistics
from app.core.models.transaction import DefaultTransaction, Transaction
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.repositories import ITransactionRepository, IWalletRepository
from app.core.schemas.transaction import TransactionRequest
from app.infra.repositories.sqlite.utils import get_cursor


class ITransactionInterceptor:
    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        pass

    def get_all_transaction(self, user: User) -> list[Transaction]:
        pass

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        pass


class ICommissionCalculator(Protocol):
    def get_balances(
        self, request_amount: int, wallet_from: Wallet, wallet_to: Wallet
    ) -> int:
        pass


@dataclass
class TransactionCalculator:
    commission_rate: float = 0.015

    def _get_commission(
        self, request_amount: int, wallet_from: Wallet, wallet_to: Wallet
    ) -> int:
        if wallet_from.user_id == wallet_to.user_id:
            return 0
        return int(request_amount * self.commission_rate)

    def get_balances(
        self, request_amount: int, wallet_from: Wallet, wallet_to: Wallet
    ) -> int:
        commission = self._get_commission(request_amount, wallet_from, wallet_to)
        total_amount = request_amount + commission
        if wallet_from.balance < total_amount:
            raise NotEnoughMoneyException()
        wallet_from.balance -= total_amount
        wallet_to.balance += request_amount
        return commission


class IStatisticsRepository(Protocol):
    def record_transaction(self, commission: int) -> None:
        pass

    def get_statistics(self) -> Statistics:
        pass


class InMemoryStatisticsRepository(IStatisticsRepository):
    statistics: Statistics

    def __init__(self) -> None:
        self.statistics = Statistics(0, 0)

    def record_transaction(self, commission: int) -> None:
        self.statistics.profit += commission
        self.statistics.total_transactions += 1

    def get_statistics(self) -> Statistics:
        return self.statistics


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


@dataclass
class TransactionInterceptor(ITransactionInterceptor):
    transaction_repository: ITransactionRepository
    wallet_repository: IWalletRepository
    calculator: ICommissionCalculator = field(default_factory=TransactionCalculator)

    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        wallet_from = self.wallet_repository.get_wallet(request.from_wallet)
        if wallet_from.user_id != user.id:
            raise WrongWalletRequestException()
        wallet_to = self.wallet_repository.get_wallet(request.to_wallet)
        commission = self.calculator.get_balances(
            request.amount, wallet_from, wallet_to
        )
        self.wallet_repository.update_wallet(wallet_from)
        self.wallet_repository.update_wallet(wallet_to)
        self.transaction_repository.add_transaction(
            DefaultTransaction(
                request.from_wallet, request.to_wallet, request.amount, commission
            )
        )
        return commission

    def get_all_transaction(self, user: User) -> list[Transaction]:
        return self.transaction_repository.find_all_transaction()

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        wallet = self.wallet_repository.get_wallet(address)
        if wallet.user_id != user.id:
            raise WrongWalletRequestException()
        return self.transaction_repository.find_transaction_by_wallet(address)
