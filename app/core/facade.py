from dataclasses import dataclass
from typing import Protocol

from app.core.interceptors.user import IUserInterceptor
from app.core.security.api_key_generator import ApiKey


class IFacade(Protocol):
    def create_user(self) -> ApiKey:
        pass


@dataclass
class Facade(IFacade):
    user_interceptor: IUserInterceptor

    def create_user(self) -> ApiKey:
        return self.user_interceptor.create_user()
