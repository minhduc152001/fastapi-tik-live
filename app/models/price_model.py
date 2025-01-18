from pydantic import BaseModel


class PriceRequest(BaseModel):
    amount_per_month: int
    total_tiktok_ids: int
    total_months: int

class PriceModel(BaseModel):
    id: str
    amount_per_month: int
    total_tiktok_ids: int
    total_months: int