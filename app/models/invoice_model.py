from datetime import datetime
from pydantic import BaseModel


class InvoiceModel(BaseModel):
    id: str
    invoice_id: str
    customer: str
    vendor: str
    total_months: int
    total_month_cost: int
    total_tiktok_ids: int
    total_amount: int
    VAT: str
    created_at: datetime