from pydantic import BaseModel


class SMSResponse(BaseModel):
    id: str
    sender: str
    msg: str