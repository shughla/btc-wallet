from dataclasses import dataclass
from typing import Optional, Protocol

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


@dataclass
class Facade(IFacade):
    user_interceptor: IUserInterceptor
    wallet_interceptor: IWalletInterceptor

    def create_user(self) -> ApiKey:
        return self.user_interceptor.create_user()

    def create_wallet(self, user: User) -> Optional[Wallet]:
        return self.wallet_interceptor.create_wallet(user)

    def authenticate(self, api_key: ApiKey) -> Optional[User]:
        return self.user_interceptor.get_user(api_key)
