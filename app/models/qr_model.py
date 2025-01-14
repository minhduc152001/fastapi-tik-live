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