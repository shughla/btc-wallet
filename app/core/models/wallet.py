from dataclasses import dataclass


@dataclass
class Wallet:
    address: int
    user_id: int
    balance: int


class DefaultWallet(Wallet):
    def __init__(self, user_id: int) -> None:
        super().__init__(-1, user_id, 100_000_000)
