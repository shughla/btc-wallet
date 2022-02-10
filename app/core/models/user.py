from dataclasses import dataclass

from app.core.security.api_key_generator import ApiKey


@dataclass
class User:
    id: int
    api_key: ApiKey
