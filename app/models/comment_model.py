from datetime import datetime
from pydantic import BaseModel

class Comment(BaseModel):
    room_id: str
    user_id: str
    msg_id: str
    customer_id: str # reference to table `customers`
    customer_name: str
    comment: str
    created_at: datetime = datetime.now()

class CommentResponse(BaseModel):
    id: str
    room_id: str
    user_id: str
    msg_id: str
    customer_id: str
    customer_name: str
    comment: str
    created_at: datetime