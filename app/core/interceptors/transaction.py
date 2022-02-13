from dataclasses import dataclass, field

from app.core.calculator import ICommissionCalculator, TransactionCalculator
from app.core.exceptions import WrongWalletRequestException
from app.core.models.transaction import DefaultTransaction, Transaction
from app.core.models.user import User
from app.core.repositories import ITransactionRepository, IWalletRepository
from app.core.schemas.transaction import TransactionRequest


class ITransactionInterceptor:
    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        pass

    def get_all_transactions(self) -> list[Transaction]:
        pass

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        pass


@dataclass
class TransactionInterceptor(ITransactionInterceptor):
    transaction_repository: ITransactionRepository
    wallet_repository: IWalletRepository
    calculator: ICommissionCalculator = field(default_factory=TransactionCalculator)

    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        wallet_from = self.wallet_repository.get_wallet(request.from_wallet)
        if wallet_from.user_id != user.id:
            raise WrongWalletRequestException(wallet_from.address)
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

    def get_all_transactions(self) -> list[Transaction]:
        return self.transaction_repository.find_all_transaction()

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        wallet = self.wallet_repository.get_wallet(address)
        if wallet.user_id != user.id:
            raise WrongWalletRequestException(address)
        return self.transaction_repository.find_transaction_by_wallet(address)
