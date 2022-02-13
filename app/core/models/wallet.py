from dataclasses import dataclass

from app.core.const import Config


@dataclass
class Wallet:
    address: int
    user_id: int
    balance: int


class DefaultWallet(Wallet):
    def __init__(self, user_id: int) -> None:
        super().__init__(-1, user_id, Config.DEFAULT_AMOUNT_ON_REGISTRATION)
