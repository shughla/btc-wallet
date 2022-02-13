from dataclasses import dataclass


class Currency:
    USD = "USD"
    BTC = "BTC"


@dataclass(frozen=True)
class CurrencyRate:
    currency: str
    rate: float
