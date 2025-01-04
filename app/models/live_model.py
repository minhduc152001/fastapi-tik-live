from pydantic import BaseModel


class LiveConnectBody(BaseModel):
    tiktok_id: str

class LiveConnectResponse(BaseModel):
    is_live: bool
    message: str
