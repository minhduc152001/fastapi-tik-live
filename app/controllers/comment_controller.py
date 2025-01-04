from fastapi import HTTPException
from jose import JWTError

from app.services.auth_service import decode_access_token, get_user_by_email
from app.services.comment_service import list_comments_by_room_id
from app.services.room_service import list_room_service


async def list_comments(token:str, room_id: str):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    list_rooms = await list_room_service(payload["id"])
    if room_id not in [room.id for room in list_rooms]:
        raise HTTPException(status_code = 403, detail = "Not included in your Rooms")
    comments = await list_comments_by_room_id(room_id)
    return comments