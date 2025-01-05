from typing import List

from app.controllers.comment_controller import list_comments
from fastapi import APIRouter, Query, Header
from app.models.comment_model import CommentResponse

comment_router = APIRouter()

@comment_router.get("/", response_description="List comments of live room", response_model=List[CommentResponse])
async def get_comments(room_id: str = Query(...), authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await list_comments(token, room_id)
