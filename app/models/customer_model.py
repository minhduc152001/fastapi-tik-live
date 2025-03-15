from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel

class CustomerBase(BaseModel):
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    profile_picture_url: str
    phone: List[str] = ()
    address: List[str] = ()
    created_at: datetime
    updated_at: datetime
class CustomerBaseResponse(BaseModel):
    id: str
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    profile_picture_url: str
    phone: List[str] = ()
    address: List[str] = ()
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

class AddLocalCustomer(BaseModel):
    customer_user_id: str
    customer_tiktok_id: str
    from_live_of_tiktok_id: str
    customer_name: str
    profile_picture_url: str

class CustomerUpdate(BaseModel):
    customer_user_id: str
    customer_tiktok_id: str
    from_live_of_tiktok_id: str
    customer_name: str
    profile_picture_url: str
    phone: Optional[str] = None
    address: Optional[str] = None

class LocalCustomerModel(BaseModel):
    id: str
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    profile_picture_url: str
    user_id: str
    from_live_of_tiktok_id: str
    phone: List[str]
    address: List[str]

class GlobalCustomerModel(BaseModel):
    id: str
    customer_user_id: str
    customer_tiktok_id: str
    customer_name: str
    profile_picture_url: str
    phone: List[str]
    address: List[str]

class FieldName(str, Enum):
    PHONE = "phone"
    ADDRESS = "address"

class DeleteRequest(BaseModel):
    field: FieldName
    elements: List[str]