from dataclasses import dataclass, field
from typing import Optional, Protocol

from app.core.interceptors.rate_converter import IRateConverter, SatoshiRateConverter
from app.core.interceptors.user import IUserInterceptor
from app.core.interceptors.wallet import IWalletInterceptor
from app.core.models.user import User
from app.core.models.wallet import Wallet
from app.core.security.api_key_generator import ApiKey


class IFacade(Protocol):
    def create_user(self) -> ApiKey:
        pass

    def create_wallet(self, user: User) -> Optional[Wallet]:
        pass

    def authenticate(self, api_key: ApiKey) -> Optional[User]:
        pass

    def get_satoshi_rate(self, currency: str) -> float:
        pass


@dataclass
class Facade(IFacade):
    user_interceptor: IUserInterceptor
    wallet_interceptor: IWalletInterceptor
    rate_converter: IRateConverter = field(default_factory=SatoshiRateConverter)

    def create_user(self) -> ApiKey:
        return self.user_interceptor.create_user()

    def create_wallet(self, user: User) -> Optional[Wallet]:
        return self.wallet_interceptor.create_wallet(user)

    def authenticate(self, api_key: ApiKey) -> Optional[User]:
        return self.user_interceptor.get_user(api_key)

    def get_satoshi_rate(self, currency: str) -> float:
        return self.rate_converter.get_rate(currency)
