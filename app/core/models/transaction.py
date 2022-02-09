from dataclasses import dataclass


@dataclass
class Transaction:
    transaction_id: int
    from_wallet: int
    to_wallet: int
    amount: int
    commission: int
