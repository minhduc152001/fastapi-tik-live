from fastapi import HTTPException
from jose import JWTError

from app.services.auth_service import decode_access_token, get_user_by_email


async def auth_middleware(token: str):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code = 401, detail = "Mã token không hợp lệ hoặc hết hạn.")
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code = 404, detail = "Không tìm thấy người dùng")
    return user

async def auth_admin_middleware(token: str):
    user = await auth_middleware(token)
    if user.get("role") == "admin":
        return user
    raise HTTPException(status_code = 403, detail = "Chỉ cho phép ADMIN.")