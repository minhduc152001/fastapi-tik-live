from typing import List

from fastapi import APIRouter, Header

from app.controllers.room_controller import list_rooms
from app.models.room_model import RoomResponse

room_routes = APIRouter()

@room_routes.get("/", response_description = "List of all rooms", status_code = 200, response_model = List[RoomResponse])
async def get_all_rooms(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await list_rooms(token)