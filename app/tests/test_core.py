import pytest

from app.core.calculator import TransactionCalculator
from app.core.exceptions import (
    MaximumWalletAmountReachedException,
    NotEnoughMoneyException,
    WrongWalletRequestException,
)
from app.core.interactors.statistics import StatisticsInteractor
from app.core.interactors.transaction import TransactionInteractor
from app.core.interactors.user import UserInteractor
from app.core.interactors.wallet import WalletInteractor
from app.core.models.currency import CurrencyRate
from app.core.models.statistics import Statistics
from app.core.models.user import User
from app.core.models.wallet import DefaultWallet, Wallet
from app.core.schemas.transaction import TransactionRequest
from app.core.schemas.wallet import WalletResponseBuilder
from app.core.security.api_key_generator import ApiKey, ApiKeyGenerator
from app.infra.repositories.inmemory.statistics import InMemoryStatisticsRepository
from app.infra.repositories.inmemory.transaction import InMemoryTransactionRepository
from app.infra.repositories.inmemory.user import InMemoryUserRepository
from app.infra.repositories.inmemory.wallet import InMemoryWalletRepository
from app.runner.setup import TEST_COMMISSION_PERCENT


def test_wallet_interactor() -> None:
    user = User(0, ApiKey("asd"))
    max_wallets = 5
    interactor = WalletInteractor(InMemoryWalletRepository(), max_wallets)
    for i in range(8):
        if i < max_wallets:
            interactor.create_wallet(user)
        else:
            try:
                interactor.create_wallet(user)
                assert False
            except MaximumWalletAmountReachedException:
                pass


def assert_statistics(stats: Statistics, profit: int, total: int) -> None:
    assert stats.profit == profit
    assert stats.total_transactions == total


def test_statistics_interactor() -> None:
    interactor = StatisticsInteractor(InMemoryStatisticsRepository())
    assert_statistics(interactor.get_statistics(), 0, 0)
    interactor.log_transaction_commission(500)
    assert_statistics(interactor.get_statistics(), 500, 1)
    interactor.log_transaction_commission(400)
    assert_statistics(interactor.get_statistics(), 900, 2)


def create_transaction(
    from_wallet: int, to_wallet: int, amount: int
) -> TransactionRequest:
    return TransactionRequest(
        from_wallet=from_wallet, to_wallet=to_wallet, amount=amount
    )


def test_transactions_interactor() -> None:
    interactor = TransactionInteractor(
        InMemoryTransactionRepository(),
        InMemoryWalletRepository(),
        TransactionCalculator(TEST_COMMISSION_PERCENT),
    )
    user1 = User(0, ApiKey("key1"))
    user2 = User(1, ApiKey("key2"))
    interactor.wallet_repository.add_wallet(Wallet(0, 0, 1000))
    interactor.wallet_repository.add_wallet(Wallet(1, 0, 500))
    interactor.wallet_repository.add_wallet(Wallet(2, 1, 500))
    assert len(interactor.get_all_transactions()) == 0
    with pytest.raises(NotEnoughMoneyException):
        assert interactor.create_transaction(user1, create_transaction(0, 1, 1001))
    with pytest.raises(WrongWalletRequestException):
        assert interactor.create_transaction(user2, create_transaction(0, 1, 1001))
    assert interactor.create_transaction(user1, create_transaction(0, 1, 500)) == 0
    assert (
        interactor.create_transaction(user2, create_transaction(2, 0, 100))
        == 100 * TEST_COMMISSION_PERCENT
    )
    assert interactor.wallet_repository.get_wallet(0).balance == 550
    assert interactor.wallet_repository.get_wallet(1).balance == 1000
    assert interactor.wallet_repository.get_wallet(2).balance == 400


def test_user_creation() -> None:
    interactor = UserInteractor(InMemoryUserRepository())
    wrong_key = ApiKey("test")
    assert interactor.get_user(wrong_key) is None
    key = interactor.create_user()
    assert interactor.get_user(key) is not None
    assert interactor.get_user(wrong_key) is None


def test_wallet_response_creator() -> None:
    wallet = Wallet(address=1, user_id=-1, balance=10)
    currencies = [
        CurrencyRate(currency="USD", rate=1),
        CurrencyRate(currency="EUR", rate=1.2),
        CurrencyRate(currency="GBP", rate=1.5),
        CurrencyRate(currency="BTC", rate=0.0001),
    ]

    wallet_response = (
        WalletResponseBuilder(wallet=wallet)
        .with_currency(currencies[0])
        .with_currency(currencies[1])
        .with_currency(currencies[2])
        .with_currency(currencies[3])
        .create()
    )

    assert wallet_response.address == 1
    assert wallet_response.balance_currencies[0].currency == "USD"
    assert wallet_response.balance_currencies[0].balance == 10
    assert wallet_response.balance_currencies[1].currency == "EUR"
    assert wallet_response.balance_currencies[1].balance == 12
    assert wallet_response.balance_currencies[2].currency == "GBP"
    assert wallet_response.balance_currencies[2].balance == 15
    assert wallet_response.balance_currencies[3].currency == "BTC"
    assert wallet_response.balance_currencies[3].balance == 0.001


def test_transaction_commission() -> None:
    wallet1 = DefaultWallet(0)
    wallet2 = DefaultWallet(1)
    wallet3 = DefaultWallet(0)
    calculator = TransactionCalculator(0.5)
    assert 500 == calculator.get_balances(1000, wallet1, wallet2)
    assert 0 == calculator.get_balances(500, wallet1, wallet3)
    with pytest.raises(NotEnoughMoneyException):
        assert calculator.get_balances(10**15, wallet1, wallet1)
        assert calculator.get_balances(10**15, wallet1, wallet2)
        assert calculator.get_balances(10**15, wallet1, wallet3)


def test_default_generator() -> None:
    keys = set()
    generator = ApiKeyGenerator()
    for i in range(10000):
        key = generator.generate_api_key()
        assert key not in keys
        keys.add(key)
