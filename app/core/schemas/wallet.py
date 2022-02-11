from dataclasses import dataclass, field

from pydantic import BaseModel

from app.core.interceptors.rate_converter import CurrencyRate
from app.core.models.wallet import Wallet


class Balance(BaseModel):  # type: ignore
    currency: str
    balance: float


class WalletResponse(BaseModel):  # type: ignore
    address: int
    amounts: list[Balance]


@dataclass
class WalletResponseBuilder:
    wallet: Wallet
    currencies: list[CurrencyRate] = field(default_factory=list)

    def with_currency(self, currency: CurrencyRate) -> "WalletResponseBuilder":
        self.currencies.append(currency)
        return self

    def create(self) -> WalletResponse:
        balance_list = []

        for currency in self.currencies:
            balance_list.append(
                Balance(
                    currency=currency.currency,
                    balance=self.wallet.balance * currency.rate,
                )
            )

        return WalletResponse(address=self.wallet.address, amounts=balance_list)
