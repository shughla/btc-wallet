from http import HTTPStatus
from typing import Any

from starlette.testclient import TestClient

from app.runner.setup import TestAppFactory

appFactory = TestAppFactory()
app = appFactory.create_app()
client = TestClient(app)


def create_user() -> Any:
    response = client.post("/user")
    headers = response.json()
    api_key = headers["api_key"]
    return api_key


def create_wallet(api_key: str) -> Any:
    response = client.post("/wallet", headers={"api-key": api_key})
    wallet_address_one = response.json()["address"]
    return wallet_address_one


def test_get_items() -> None:
    response = client.post("/user")
    assert response.status_code == HTTPStatus.CREATED
    assert (
        len(response.json()["api_key"]) >= 16
    )  # key should be at least 16 symbols for randomness


def test_get_wallet() -> None:
    response = client.post("/user")
    headers = response.json()
    response = client.post("/wallet", headers={"api-key": headers["api_key"]})
    assert response.status_code == HTTPStatus.CREATED
    address_one = response.json()["address"]
    response = client.get(
        f"/wallet/{address_one}", headers={"api-key": headers["api_key"]}
    )
    assert response.status_code == HTTPStatus.OK


def test_get_wallet_wrong_user() -> None:
    # todo
    pass


def test_transaction() -> None:
    key_one = create_user()
    response = client.post("/wallet", headers={"api-key": key_one})
    wallet_address_one = response.json()["address"]

    key_two = create_user()
    response = client.post("/wallet", headers={"api-key": key_two})
    wallet_address_two = response.json()["address"]
    headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "api-key": key_one,
    }
    transaction = {
        "from_wallet": wallet_address_one,
        "to_wallet": wallet_address_two,
        "amount": 2000,
    }
    response = client.post("/transaction", headers=headers, json=transaction)
    assert response.status_code == HTTPStatus.CREATED


def test_transaction_limit() -> None:
    key_one = create_user()
    wallet_address_one = create_wallet(key_one)

    key_two = create_user()
    wallet_address_two = create_wallet(key_two)
    headers = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "api-key": key_one,
    }
    transaction = {
        "from_wallet": wallet_address_one,
        "to_wallet": wallet_address_two,
        "amount": 2000000000,
    }
    response = client.post("/transaction", headers=headers, json=transaction)
    assert response.status_code == HTTPStatus.BAD_REQUEST


def assert_equal_balances(
    key_one: str, key_two: str, wallet_address_one: int, wallet_address_two: int
) -> None:
    response = client.get(f"/wallet/{wallet_address_one}", headers={"api-key": key_one})
    wallet_one = response.json()
    response = client.get(f"/wallet/{wallet_address_two}", headers={"api-key": key_two})
    wallet_two = response.json()
    assert wallet_one["balance_currencies"] == wallet_two["balance_currencies"]


def test_transactions() -> None:
    key_one = create_user()
    wallet_address_one = create_wallet(key_one)

    key_two = create_user()
    wallet_address_two = create_wallet(key_two)

    assert_equal_balances(key_one, key_two, wallet_address_one, wallet_address_two)
    response = client.get("/transaction", headers={"api-key": key_one})
    initial_transaction_len = len(response.json())

    headers_one = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "api-key": key_one,
    }
    transaction = {
        "from_wallet": wallet_address_one,
        "to_wallet": wallet_address_two,
        "amount": 2000,
    }
    response = client.post("/transaction", headers=headers_one, json=transaction)
    assert response.status_code == HTTPStatus.CREATED
    headers = {
        "Accept": "application/json",
        "api-key": key_one,
    }
    response = client.get("/transaction", headers=headers)
    transactions = response.json()
    assert len(transactions) == initial_transaction_len + 1
    assert transactions[initial_transaction_len]["from_wallet"] == wallet_address_one
    assert transactions[initial_transaction_len]["to_wallet"] == wallet_address_two
    assert transactions[initial_transaction_len]["amount"] == 2000

    transaction = {
        "from_wallet": wallet_address_two,
        "to_wallet": wallet_address_one,
        "amount": 2000,
    }
    headers_two = {
        "Accept": "application/json",
        "Content-type": "application/json",
        "api-key": key_two,
    }
    response = client.post("/transaction", headers=headers_two, json=transaction)
    assert response.status_code == HTTPStatus.CREATED
    response = client.get("/transaction", headers=headers_two)
    transactions = response.json()
    assert len(transactions) == initial_transaction_len + 2
    assert transactions[initial_transaction_len]["from_wallet"] == wallet_address_one
    assert transactions[initial_transaction_len]["to_wallet"] == wallet_address_two
    assert transactions[initial_transaction_len]["amount"] == 2000
    assert (
        transactions[initial_transaction_len + 1]["from_wallet"] == wallet_address_two
    )
    assert transactions[initial_transaction_len + 1]["to_wallet"] == wallet_address_one
    assert transactions[initial_transaction_len + 1]["amount"] == 2000

    assert_equal_balances(key_one, key_two, wallet_address_one, wallet_address_two)
    response = client.get(
        f"/wallet/{wallet_address_two}/transaction", headers=headers_two
    )
    transactions_two = response.json()

    response = client.get(
        f"/wallet/{wallet_address_one}/transaction", headers=headers_one
    )
    transactions_one = response.json()
    assert len(transactions_one) == len(transactions_two)
