from http import HTTPStatus

from starlette.testclient import TestClient

from app.runner.setup import TestAppFactory

appFactory = TestAppFactory()
app = appFactory.create_app()
client = TestClient(app)


def test_get_items() -> None:
    print(app)
    print(client)
    response = client.post("/user")
    print(response)
    assert response.status_code == HTTPStatus.CREATED
    assert (
        len(response.json()["api_key"]) >= 16
    )  # key should be at least 16 symbols for randomness
