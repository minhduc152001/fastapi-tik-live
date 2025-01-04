from fastapi import HTTPException
from jose import JWTError

from app.services.auth_service import decode_access_token, get_user_by_email
from app.services.room_service import list_room_service


async def list_rooms(token: str):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    rooms = await list_room_service(payload["id"])
    return rooms