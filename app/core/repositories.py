from typing import Optional, Protocol

from app.core.models.statistics import Statistics
from app.core.models.transaction import Transaction
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.security.api_key_generator import ApiKey


class IUserRepository(Protocol):
    def add_user(self, api_key: ApiKey) -> None:
        pass

    def find(self, api_key: ApiKey) -> Optional[User]:
        pass


class IWalletRepository(Protocol):
    def get_wallets(self, user: User) -> list[Wallet]:
        pass

    def add_wallet(self, wallet: Wallet) -> Wallet:
        pass

    def get_wallet(self, address: int) -> Wallet:
        pass

    def update_wallet(self, wallet: Wallet) -> None:
        pass


class ITransactionRepository(Protocol):
    def add_transaction(self, request: Transaction) -> None:
        pass

    def find_all_transaction(self) -> list[Transaction]:
        pass

    def find_transaction_by_wallet(self, address: int) -> list[Transaction]:
        pass


class IStatisticsRepository(Protocol):
    def record_transaction(self, commission: int) -> None:
        pass

    def get_statistics(self) -> Statistics:
        pass
