from dataclasses import dataclass
from typing import Protocol

from app.core.const import Config
from app.core.exceptions import NotEnoughMoneyException
from app.core.models.wallet import Wallet


class ICommissionCalculator(Protocol):
    def get_balances(
        self, request_amount: int, wallet_from: Wallet, wallet_to: Wallet
    ) -> int:
        pass


@dataclass
class TransactionCalculator:
    commission_rate: float = Config.DEFAULT_COMMISSION_RATE

    def _get_commission(
        self, request_amount: int, wallet_from: Wallet, wallet_to: Wallet
    ) -> int:
        if wallet_from.user_id == wallet_to.user_id:
            return self._calculate_commission(request_amount, 0)
        return self._calculate_commission(request_amount, self.commission_rate)

    def _calculate_commission(self, request_amount: int, commission_rate: float) -> int:
        return int(request_amount * commission_rate)

    def get_balances(
        self, request_amount: int, wallet_from: Wallet, wallet_to: Wallet
    ) -> int:
        commission = self._get_commission(request_amount, wallet_from, wallet_to)
        total_amount = request_amount + commission
        if wallet_from.balance < total_amount:
            raise NotEnoughMoneyException(wallet_from.address)
        wallet_from.balance -= total_amount
        wallet_to.balance += request_amount
        return commission
