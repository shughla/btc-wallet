from dataclasses import dataclass, field
from datetime import datetime, timedelta

import requests


class Currency:
    USD = "USD"
    BTC = "BTC"


@dataclass(frozen=True)
class CurrencyRate:
    currency: str
    rate: float


class IRateConverter:
    def get_rate(self, currency: str) -> CurrencyRate:
        pass


BTC_FRACTION = float(10**-8)


class SatoshiRateConverter(IRateConverter):
    CRYPTOCOMPARE_ENDPOINT = (
        "https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=%s"
    )

    def get_rate(self, currency: str) -> CurrencyRate:
        quote_url = self.CRYPTOCOMPARE_ENDPOINT % (Currency.BTC, currency.upper())
        response = requests.get(quote_url)
        btc_value = response.json().get(currency.upper())
        amount = 1
        fiat_value = float(amount * BTC_FRACTION) * float(btc_value)
        currency_rate = CurrencyRate(currency=currency, rate=fiat_value)
        return currency_rate


@dataclass
class DummySatoshiRateConverter(IRateConverter):
    custom_rate: float = 1.5

    def get_rate(self, currency: str) -> CurrencyRate:
        if currency == "BTC":
            return CurrencyRate("BTC", BTC_FRACTION)
        else:
            return CurrencyRate(currency, self.custom_rate)


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
