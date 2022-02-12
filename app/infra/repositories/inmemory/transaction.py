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
