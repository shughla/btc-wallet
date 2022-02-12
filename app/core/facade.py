from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Optional, Protocol

from app.core.interceptors.rate_converter import (  # CachedRateConverter,
    CurrencyRate,
    IRateConverter,
    SatoshiRateConverter,
)
from app.core.interceptors.transaction import (
    IStatisticsRepository,
    ITransactionInterceptor,
)
from app.core.interceptors.user import IUserInterceptor
from app.core.interceptors.wallet import IWalletInterceptor
from app.core.models.statistics import Statistics
from app.core.models.transaction import Transaction
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.schemas.transaction import TransactionRequest
from app.core.security.api_key_generator import ApiKey


def log_transaction(func: Any) -> Any:
    statistics_repository: IStatisticsRepository

    @wraps(func)
    def transaction_decorator(
        self: "Facade", user: User, request: TransactionRequest
    ) -> int:
        commission: int = func(
            self, user, request
        )  # throws exception if transaction fails
        self.statistics_interceptor.log_transaction_commission(commission)
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

    def get_all_transaction(self, user: User) -> list[Transaction]:
        pass

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        pass

    def get_statistics(self) -> Statistics:
        pass


class IStatisticsInterceptor(Protocol):
    def log_transaction_commission(self, commission: int) -> None:
        pass

    def get_statistics(self) -> Statistics:
        pass


@dataclass
class StatisticsInterceptor(IStatisticsInterceptor):
    statistics_repository: IStatisticsRepository

    def log_transaction_commission(self, commission: int) -> None:
        self.statistics_repository.record_transaction(commission)

    def get_statistics(self) -> Statistics:
        return self.statistics_repository.get_statistics()


@dataclass
class Facade(IFacade):
    user_interceptor: IUserInterceptor
    wallet_interceptor: IWalletInterceptor
    transaction_interceptor: ITransactionInterceptor
    statistics_interceptor: IStatisticsInterceptor
    rate_converter: IRateConverter = field(default_factory=SatoshiRateConverter)

    def create_user(self) -> ApiKey:
        return self.user_interceptor.create_user()

    def create_wallet(self, user: User) -> Optional[Wallet]:
        return self.wallet_interceptor.create_wallet(user)

    def authenticate(self, api_key: ApiKey) -> Optional[User]:
        return self.user_interceptor.get_user(api_key)

    def get_satoshi_rate(self, currency: str) -> CurrencyRate:
        return self.rate_converter.get_rate(currency)

    def get_wallet(self, user: User, address: int) -> Wallet:
        return self.wallet_interceptor.get_wallet(user, address)

    @log_transaction
    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        return self.transaction_interceptor.create_transaction(user, request)

    def get_all_transaction(self, user: User) -> list[Transaction]:
        return self.transaction_interceptor.get_all_transaction(user)

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        return self.transaction_interceptor.get_wallet_transactions(user, address)

    def get_statistics(self) -> Statistics:
        return self.statistics_interceptor.get_statistics()
