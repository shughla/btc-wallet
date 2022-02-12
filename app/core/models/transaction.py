from dataclasses import dataclass


@dataclass
class Transaction:
    transaction_id: int
    from_wallet: int
    to_wallet: int
    amount: int
    commission: int


class DefaultTransaction(Transaction):
    def __init__(self, from_wallet: int, to_wallet: int, amount: int, commission: int):
        super().__init__(-1, from_wallet, to_wallet, amount, commission)
