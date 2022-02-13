from dataclasses import dataclass

from app.core.const import Config
from app.core.models.currency import CurrencyRate
from app.core.rate_converter import IRateConverter


@dataclass
class DummySatoshiRateConverter(IRateConverter):
    custom_rate: float = 1.5

    def get_rate(self, currency: str) -> CurrencyRate:
        if currency == "BTC":
            return CurrencyRate("BTC", 1 / Config.BTC_TO_SATOSHI)
        else:
            return CurrencyRate(currency, self.custom_rate)
