from pydantic import BaseModel


class WalletResponse(BaseModel):  # type: ignore
    address: int
    balance_usd: float
    balance_bitcoin: float
