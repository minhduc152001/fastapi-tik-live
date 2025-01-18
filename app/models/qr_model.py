from datetime import datetime

from pydantic import BaseModel


class QRRequest(BaseModel):
    bank_code: str
    account_number: str
    amount_per_month: int
    subscription_months: int

class QRResponse(BaseModel):
    bank_name: str
    payment_description: str
    url: str

class QRModel(BaseModel):
    id: str
    bank_code: str
    account_number: str
    amount_per_month: int
    subscription_months: int
    bank_name: str
    user_email: str
    payment_description: str
    total_amount: int
    created_at: datetime