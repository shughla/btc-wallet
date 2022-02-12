from pydantic import BaseModel


class TransactionRequest(BaseModel):
    from_wallet: int
    to_wallet: int
    amount: int


class TransactionResponse(BaseModel):
    from_wallet: int
    to_wallet: int
    amount: int
    commission: int
