from fastapi import HTTPException, BackgroundTasks
from jose import JWTError
from app.services.auth_service import decode_access_token, get_user_by_email
from app.services.tiktok_service import connect_live_service

async def connect_live(token: str, tiktok_id: str, background_tasks: BackgroundTasks):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not tiktok_id in user["tiktok_ids"]:
        raise HTTPException(status_code=403, detail="Not include this TikTok ID")

    result = await connect_live_service(tiktok_id, payload["id"], background_tasks)
    return result
