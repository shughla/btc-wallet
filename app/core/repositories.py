from typing import Optional, Protocol

from app.core.models.user import User
from app.core.security.api_key_generator import ApiKey


class IUserRepository(Protocol):
    def add_user(self, api_key: ApiKey) -> None:
        pass

    def find(self, api_key: ApiKey) -> Optional[User]:
        pass
