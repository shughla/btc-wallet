import sqlite3
from http import HTTPStatus

from starlette.testclient import TestClient

from app.core.exceptions import DuplicateUserApiKeyException
from app.core.security.api_key_generator import ApiKey
from app.infra.repositories.inmemory.user import InMemoryUserRepository
from app.infra.repositories.sqlite.user import SQLiteUserRepository
from app.runner.setup import TestAppFactory

appFactory = TestAppFactory()
app = appFactory.create_app()
client = TestClient(app)


def test_get_items() -> None:
    response = client.post("/user")
    assert response.status_code == HTTPStatus.CREATED
    assert (
        len(response.json()["api_key"]) >= 16
    )  # key should be at least 16 symbols for randomness


def test_same_api_key() -> None:
    repo = InMemoryUserRepository()
    key = ApiKey("asdasdasd")
    not_added_key = ApiKey("asd")
    repo.add_user(key)
    assert repo.find(key) is not None
    assert repo.find(not_added_key) is None


def test_sqlite_user_repository() -> None:
    test_connection = sqlite3.connect(":memory:", check_same_thread=False)
    repo = SQLiteUserRepository(test_connection)
    key = ApiKey("test")
    repo.add_user(key)
    try:
        repo.add_user(key)
        assert False
    except DuplicateUserApiKeyException:
        pass
    assert repo.find(key) is not None
