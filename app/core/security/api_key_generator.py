import secrets
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ApiKey:
    api_key: str


class IApiKeyGenerator(Protocol):
    def generate_api_key(self) -> ApiKey:
        pass


class ApiKeyGenerator(IApiKeyGenerator):
    def generate_api_key(self) -> ApiKey:
        return ApiKey(secrets.token_urlsafe(16))


def test_default_generator() -> None:
    keys = set()
    generator = ApiKeyGenerator()
    for i in range(10000):
        key = generator.generate_api_key()
        assert key not in keys
        keys.add(key)
