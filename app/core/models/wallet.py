from dataclasses import dataclass


@dataclass
class Wallet:
    wallet_id: int
    user_id: int
    balance: int
