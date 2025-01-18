from datetime import datetime
from pydantic import BaseModel


class InvoiceModel(BaseModel):
    id: str
    invoice_id: str
    customer: str
    vendor: str
    amount_per_month: int
    subscription_months: int
    total_amount: int
    VAT: str
    created_at: datetime