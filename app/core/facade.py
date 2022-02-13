from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Optional, Protocol

from app.core.interactors.statistics import IStatisticsInteractor
from app.core.interactors.transaction import ITransactionInteractor
from app.core.interactors.user import IUserInteractor
from app.core.interactors.wallet import IWalletInteractor
from app.core.models.currency import CurrencyRate
from app.core.models.statistics import Statistics
from app.core.models.transaction import Transaction
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.rate_converter import IRateConverter, SatoshiRateConverter
from app.core.schemas.transaction import TransactionRequest
from app.core.security.api_key_generator import ApiKey


def log_transaction(func: Any) -> Any:
    @wraps(func)
    def transaction_decorator(
        self: "Facade", user: User, request: TransactionRequest
    ) -> int:
        commission: int = func(
            self, user, request
        )  # throws exception if transaction fails
        self.statistics_interactor.log_transaction_commission(commission)
        return commission

    return transaction_decorator


class IFacade(Protocol):
    def create_user(self) -> ApiKey:
        pass

    def create_wallet(self, user: User) -> Optional[Wallet]:
        pass

    def authenticate(self, api_key: ApiKey) -> Optional[User]:
        pass

    def get_satoshi_rate(self, currency: str) -> CurrencyRate:
        pass

    def get_wallet(self, user: User, address: int) -> Wallet:
        pass

    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        pass

    def get_all_transactions(self) -> list[Transaction]:
        pass

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        pass

    def get_statistics(self) -> Statistics:
        pass


@dataclass
class Facade(IFacade):
    user_interactor: IUserInteractor
    wallet_interactor: IWalletInteractor
    transaction_interactor: ITransactionInteractor
    statistics_interactor: IStatisticsInteractor
    rate_converter: IRateConverter = field(default_factory=SatoshiRateConverter)

    def create_user(self) -> ApiKey:
        return self.user_interactor.create_user()

    def create_wallet(self, user: User) -> Optional[Wallet]:
        return self.wallet_interactor.create_wallet(user)

    def authenticate(self, api_key: ApiKey) -> Optional[User]:
        return self.user_interactor.get_user(api_key)

    def get_satoshi_rate(self, currency: str) -> CurrencyRate:
        return self.rate_converter.get_rate(currency)

    def get_wallet(self, user: User, address: int) -> Wallet:
        return self.wallet_interactor.get_wallet(user, address)

    @log_transaction
    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        return self.transaction_interactor.create_transaction(user, request)

    def get_all_transactions(self) -> list[Transaction]:
        return self.transaction_interactor.get_all_transactions()

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        return self.transaction_interactor.get_wallet_transactions(user, address)

    def get_statistics(self) -> Statistics:
        return self.statistics_interactor.get_statistics()
