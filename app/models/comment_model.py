from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class Comment(BaseModel):
    room_id: str
    user_id: str
    msg_id: str
    from_live_of_tiktok_id: str
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    comment: str
    profile_picture_url: str
    check_store_customer: bool = False
    created_at: datetime

class CommentResponse(BaseModel):
    id: str
    room_id: str
    user_id: str
    msg_id: str
    from_live_of_tiktok_id: str
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    comment: str
    profile_picture_url: str
    check_store_customer: bool
    created_at: datetime
    has_global_phone: Optional[bool] = None
    has_local_phone: Optional[bool] = None