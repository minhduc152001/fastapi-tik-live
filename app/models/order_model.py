from datetime import datetime
from pydantic import BaseModel

class Order(BaseModel):
    room_id: str
    from_live_of_tiktok_id: str
    customer_user_id: str

class OrderDetail(BaseModel):
    id: str
    room_id: str
    from_live_of_tiktok_id: str
    customer_user_id: str
    customer_name: str
    phone: str | None
    address: str | None
    created_at: datetime