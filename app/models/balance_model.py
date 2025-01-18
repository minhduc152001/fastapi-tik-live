from datetime import datetime

from pydantic import BaseModel


class BalanceMovementBase(BaseModel):
    id: str
    account_number: str
    amount: int
    transaction_time: datetime
    current_balance: int
    payment_description:str