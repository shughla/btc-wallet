from dataclasses import dataclass, field

from app.core.models.transaction import Transaction
from app.core.repositories import ITransactionRepository


@dataclass
class InMemoryTransactionRepository(ITransactionRepository):
    transactions: list[Transaction] = field(default_factory=list)

    def add_transaction(self, request: Transaction) -> None:
        index = len(self.transactions) + 1
        request.transaction_id = index
        self.transactions.append(request)

    def find_all_transaction(self) -> list[Transaction]:
        return list(self.transactions)

    def find_transaction_by_wallet(self, address: int) -> list[Transaction]:
        return list(
            filter(
                lambda x: x.from_wallet == address or x.to_wallet == address,
                self.transactions,
            )
        )
