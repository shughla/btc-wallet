from dataclasses import dataclass, field
from typing import Protocol

from app.core.exceptions import NotEnoughMoneyException, WrongWalletRequestException
from app.core.models.transaction import DefaultTransaction, Transaction
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.repositories import ITransactionRepository, IWalletRepository
from app.core.schemas.transaction import TransactionRequest


class ITransactionInterceptor:
    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        pass

    def get_all_transaction(self, user: User) -> list[Transaction]:
        pass


class ICommissionCalculator(Protocol):
    def get_balances(
        self, request_amount: int, wallet_from: Wallet, wallet_to: Wallet
    ) -> int:
        pass


class TransactionCalculator:
    commission_rate = 0.015

    def _get_commission(
        self, request_amount: int, address_from: int, address_to: int
    ) -> int:
        if address_from == address_to:
            return 0
        return int(request_amount * self.commission_rate)

    def get_balances(
        self, request_amount: int, wallet_from: Wallet, wallet_to: Wallet
    ) -> int:
        commission = self._get_commission(
            request_amount, wallet_from.address, wallet_to.address
        )
        total_amount = request_amount + commission
        if wallet_from.balance < total_amount:
            raise NotEnoughMoneyException()
        wallet_from.balance -= total_amount
        wallet_to.balance += request_amount
        return commission


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
