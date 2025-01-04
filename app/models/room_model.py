from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class Room(BaseModel):
    room_str_id: str
    is_live: bool
    title: str
    user_id: str
    tiktok_id: str
    nickname: str
    ended_at: datetime | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class RoomResponse(BaseModel):
    id: str
    room_str_id: str
    is_live: bool
    title: str
    user_id: str
    tiktok_id: str
    nickname: str
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime

class RoomUpdateRequest(BaseModel):
    is_live: Optional[bool] = None
    ended_at: Optional[datetime] = None
    updated_at: datetime = datetime.now()