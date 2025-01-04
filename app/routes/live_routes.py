from fastapi import APIRouter, Header

from app.controllers.live_controller import connect_live
from app.models.live_model import LiveConnectBody, LiveConnectResponse

live_routes = APIRouter()

@live_routes.post("/", response_description="Connect livestream", status_code=200, response_model=LiveConnectResponse)
async def live_connect(live_connect: LiveConnectBody, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    tiktok_id = live_connect.tiktok_id

    return await connect_live(token, tiktok_id)