from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

class CustomerBase(BaseModel):
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    profile_picture_url: str
    phone: List[str] = ()
    address: str | None = None
    created_at: datetime
    updated_at: datetime
class CustomerBaseResponse(BaseModel):
    id: str
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    profile_picture_url: str
    phone: List[str] = ()
    address: str | None
    created_at: datetime
    updated_at: datetime

class LocalCustomer(CustomerBase):
    user_id: str
    from_live_of_tiktok_id: str
class LocalCustomerResponse(CustomerBaseResponse):
    user_id: str
    from_live_of_tiktok_id: str

class GlobalCustomer(CustomerBase):
    pass
class GlobalCustomerResponse(CustomerBaseResponse):
    pass

class CustomerUpdate(BaseModel):
    customer_user_id: str
    customer_tiktok_id: str
    from_live_of_tiktok_id: str
    customer_name: str
    profile_picture_url: str
    phone: Optional[str] = None
    address: Optional[str] = None