from typing import List, Optional

from app.controllers.comment_controller import list_comments
from fastapi import APIRouter, Query, Header
from app.models.comment_model import CommentResponse

comment_router = APIRouter()

@comment_router.get(
    "/",
    response_description="List comments of live room",
    response_model=List[CommentResponse]
)
async def get_comments(
    room_id: str = Query(...),
    customer_user_id: Optional[str] = Query(None, description="Filter by customer user ID"),
    skip: Optional[int] = Query(None, ge=0, description="Number of records to skip (pagination)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of records to return"),
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    return await list_comments(token, room_id, customer_user_id, skip, limit)
