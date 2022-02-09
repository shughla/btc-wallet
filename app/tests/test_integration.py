from http import HTTPStatus

from starlette.testclient import TestClient

from app.tests.asgi import app

client = TestClient(app)


def test_get_items() -> None:
    response = client.post("/user")
    assert response.status_code == HTTPStatus.CREATED
    assert (
        len(response.json()["api_key"]) >= 16
    )  # key should be at least 16 symbols for randomness
