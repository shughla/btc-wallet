from dataclasses import dataclass
from typing import Protocol

from app.core.repositories import IUserRepository
from app.core.security.api_key_generator import ApiKey, IApiKeyGenerator


class IUserInterceptor(Protocol):
    def create_user(self) -> ApiKey:
        pass


@dataclass
class UserInterceptor(IUserInterceptor):

    repository: IUserRepository
    generator: IApiKeyGenerator

    def create_user(self) -> ApiKey:
        key = self.generator.generate_api_key()
        self.repository.add_user(key)
        return key
