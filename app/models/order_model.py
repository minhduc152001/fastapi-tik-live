from datetime import datetime
from typing import List

from pydantic import BaseModel

# class Order(BaseModel):
#     room_id: str
#     msg_id: str
#     from_live_of_tiktok_id: str
#     customer_user_id: str
#     customer_tiktok_id: str
#     customer_name: str
#     comment: str
#
# class OrderDetail(BaseModel):
#     id: str
#     room_id: str
#     msg_id: str
#     from_live_of_tiktok_id: str
#     customer_user_id: str
#     customer_tiktok_id: str
#     customer_name: str
#     comment: str
#     phone: List[str] | None
#     address: List[str] | None
#     user_id: str
#     live_title: str
#     live_started_at: datetime
#     created_at: datetime
#     updated_at: datetime

class SubOrder(BaseModel):
    msg_id: str
    comment: str
    commented_at: datetime

class OrderCreateRequest(BaseModel):
    room_id: str
    customer_user_id: str
    from_live_of_tiktok_id: str
    customer_tiktok_id: str
    customer_name: str
    sub_order: SubOrder

class Order(BaseModel):
    id: str
    room_id: str
    from_live_of_tiktok_id: str
    user_id: str
    live_title: str
    live_started_at: datetime
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    sub_orders: List[SubOrder]
    phone: List[str] | None
    address: List[str] | None
    created_at: datetime
    updated_at: datetime
