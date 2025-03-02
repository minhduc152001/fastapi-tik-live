from datetime import datetime
from pydantic import BaseModel

class QRRequest(BaseModel):
    bank_code: str
    account_number: str
    total_tiktok_ids: int = 1
    total_month_cost: int = 0
    total_months: int = 0

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