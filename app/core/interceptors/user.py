from dataclasses import dataclass, field
from typing import Optional, Protocol

from app.core.exceptions import DuplicateUserApiKeyException
from app.core.models.user import User
from app.core.repositories import IUserRepository
from app.core.security.api_key_generator import (
    ApiKey,
    ApiKeyGenerator,
    IApiKeyGenerator,
)


class IUserInterceptor(Protocol):
    def create_user(self) -> ApiKey:
        pass

    def get_user(self, api_key: ApiKey) -> Optional[User]:
        pass


@dataclass
class UserInterceptor(IUserInterceptor):
    repository: IUserRepository
    generator: IApiKeyGenerator = field(default_factory=ApiKeyGenerator)

    def create_user(self) -> ApiKey:
        key = self.generator.generate_api_key()
        if self.repository.find(key) is not None:
            raise DuplicateUserApiKeyException()
        self.repository.add_user(key)
        return key

    def get_user(self, api_key: ApiKey) -> Optional[User]:
        return self.repository.find(api_key)
