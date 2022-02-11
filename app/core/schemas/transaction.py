from pydantic import BaseModel


class TransactionRequest(BaseModel):  # type: ignore
    address_from: int
    address_to: int
    amount: int


class TransactionResponse(BaseModel):  # type: ignore
    paid_amount: int
