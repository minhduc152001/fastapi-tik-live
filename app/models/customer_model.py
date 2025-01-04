from datetime import datetime

from pydantic import BaseModel


class Customer(BaseModel):
    user_id: str # reference to table `users`
    tiktok_user_id: str # "12389h2r3f23"
    tiktok_id: str # "bunvakem"
    display_name: str # "Bun va Kem"
    profile_picture_url: str
    phone: str | None = None
    address: str | None = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class CustomerResponse(BaseModel):
    id: str
    user_id: str
    tiktok_user_id: str
    tiktok_id: str  # "bunvakem"
    display_name: str  # "Bun va Kem"
    profile_picture_url: str
    phone: str | None
    address: str | None
    created_at: datetime
    updated_at: datetime