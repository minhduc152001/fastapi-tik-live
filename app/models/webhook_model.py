from pydantic import BaseModel


class RetrieveWebhookBase(BaseModel):
    sender: str
    msg: str

class CheckTransaction(BaseModel):
    transferred: bool