from dataclasses import dataclass, field
from typing import Optional, Protocol

from app.core.interceptors.rate_converter import (
    CachedRateConverter,
    CurrencyRate,
    IRateConverter,
)
from app.core.interceptors.transaction import ITransactionInterceptor
from app.core.interceptors.user import IUserInterceptor
from app.core.interceptors.wallet import IWalletInterceptor
from app.core.models.transaction import Transaction
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.schemas.transaction import TransactionRequest
from app.core.security.api_key_generator import ApiKey


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


@dataclass
class Facade(IFacade):
    user_interceptor: IUserInterceptor
    wallet_interceptor: IWalletInterceptor
    transaction_interceptor: ITransactionInterceptor
    rate_converter: IRateConverter = field(default_factory=CachedRateConverter)

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

    def create_transaction(self, user: User, request: TransactionRequest) -> int:
        return self.transaction_interceptor.create_transaction(user, request)

    def get_all_transaction(self, user: User) -> list[Transaction]:
        return self.transaction_interceptor.get_all_transaction(user)

    def get_wallet_transactions(self, user: User, address: int) -> list[Transaction]:
        return self.transaction_interceptor.get_wallet_transactions(user, address)
