from typing import Optional

from fastapi import HTTPException
from jose import JWTError

from app.services.auth_service import decode_access_token, get_user_by_email
from app.services.comment_service import list_comments_by_room_id
from app.services.room_service import list_room_service


async def list_comments(token:str, room_id: str, customer_user_id: Optional[str] = None, skip: Optional[int] = None, limit: Optional[int] = None):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Mã token không hợp lệ hoặc hết hạn.")
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    list_rooms = await list_room_service(payload["id"])
    if room_id not in [room.id for room in list_rooms]:
        raise HTTPException(status_code = 403, detail = "Không tìm thấy ID phòng trong dữ liệu của bạn")
    comments = await list_comments_by_room_id(room_id, customer_user_id, skip, limit)
    return comments