from dataclasses import dataclass, field
from datetime import datetime, timedelta

import requests

from app.core.const import Config
from app.core.models.currency import Currency, CurrencyRate


class IRateConverter:
    def get_rate(self, currency: str) -> CurrencyRate:
        pass


class SatoshiRateConverter(IRateConverter):
    CRYPTOCOMPARE_ENDPOINT = (
        "https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=%s"
    )

    def get_rate(self, currency: str) -> CurrencyRate:
        quote_url = self.CRYPTOCOMPARE_ENDPOINT % (Currency.BTC, currency.upper())
        response = requests.get(quote_url)
        btc_value = response.json().get(currency.upper())
        amount = 1
        fiat_value = float(amount / Config.BTC_TO_SATOSHI) * float(btc_value)
        currency_rate = CurrencyRate(currency=currency, rate=fiat_value)
        return currency_rate


cache: dict[str, tuple[CurrencyRate, datetime]] = dict()
CACHE_TIMEDELTA = timedelta(seconds=10)


@dataclass
class CachedRateConverter(IRateConverter):
    rateConverter: IRateConverter = field(default_factory=SatoshiRateConverter)

    def get_rate(self, currency: str) -> CurrencyRate:
        rate_datetime = cache.get(currency)
        if rate_datetime is not None:
            rate, time = rate_datetime
            if time > datetime.now() - CACHE_TIMEDELTA:
                return rate
            else:
                cache.pop(currency)

        currency_rate = self.rateConverter.get_rate(currency)

        cache[currency] = (currency_rate, datetime.now())
        return currency_rate
