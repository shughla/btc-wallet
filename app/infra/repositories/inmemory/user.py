from dataclasses import dataclass, field
from typing import Optional

from app.core.exceptions import DuplicateUserApiKeyException
from app.core.models.user import User
from app.core.repositories import IUserRepository
from app.core.security.api_key_generator import ApiKey


@dataclass
class InMemoryUserRepository(IUserRepository):
    users: list[User] = field(default_factory=list)

    def add_user(self, api_key: ApiKey) -> None:
        if self.find(api_key):
            raise DuplicateUserApiKeyException()
        index = len(self.users)
        self.users.append(User(id=index, api_key=api_key))

    def find(self, api_key: ApiKey) -> Optional[User]:
        for elem in self.users:
            if elem.api_key == api_key:
                return elem
        return None
