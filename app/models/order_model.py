from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class Order(BaseModel):
    room_id: str
    msg_id: str
    from_live_of_tiktok_id: str
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    comment: str

class OrderDetail(BaseModel):
    id: str
    room_id: str
    msg_id: str
    from_live_of_tiktok_id: str
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    comment: str
    phone: List[str] | None
    address: List[str] | None
    user_id: str
    live_title: str
    live_started_at: datetime
    created_at: datetime
    updated_at: datetime
