from pydantic import BaseModel


class PriceRequest(BaseModel):
    total_month_cost: int
    total_months: int

class PriceModel(BaseModel):
    id: str
    total_month_cost: int
    total_months: int