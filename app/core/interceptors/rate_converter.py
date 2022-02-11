from dataclasses import dataclass

import requests


class Currency:
    USD = "USD"
    BTC = "BTC"


@dataclass
class CurrencyRate:
    currency: str
    rate: float


class IRateConverter:
    def get_rate(self, currency: str) -> float:
        pass


CRYPTOCOMPARE_ENDPOINT = "https://min-api.cryptocompare.com/data/price?fsym=%s&tsyms=%s"
COINDESK_ENDPOINT = "http://api.coindesk.com/v2/bpi/currentprice.json"
BTC_FRACTION = float(10 ** -8)


@dataclass
class SatoshiRateConverter(IRateConverter):
    def get_rate(self, currency: str) -> float:
        amount = 1
        quote_url = CRYPTOCOMPARE_ENDPOINT % ("BTC", currency.upper())
        response = requests.get(quote_url)
        btc_value = response.json().get(currency.upper())
        fiat_value = float(amount * BTC_FRACTION) * float(btc_value)
        return fiat_value
