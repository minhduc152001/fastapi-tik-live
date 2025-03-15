from fastapi import HTTPException
from jose import JWTError

from app.middlewares.auth_middleware import auth_admin_middleware
from app.services.auth_service import create_user, authenticate_user, generate_access_token, decode_access_token, \
    get_user_by_email, get_users, update_user_info, delete_user_service, update_admin_user_info
from app.models.user_model import User, UserResponse, UserLogin, UserLoginResponse, UserUpdateRequest, UserSignUp, \
    AdminUpdateUserRequest


async def signup(user):
    new_user = await create_user(user)
    return UserResponse(
        id=new_user["_id"],
        email=new_user["email"],
        phone=new_user["phone"],
        tiktok_ids=new_user.get("tiktok_ids", []),
        role=new_user["role"],
        max_tiktok_id_slots=new_user.get("max_tiktok_id_slots", 0),
        subscription_expired_at=new_user["subscription_expired_at"] or None,
        created_at = new_user["created_at"],
    )

async def login(body: UserLogin):
    email = body.email
    password = body.password
    user = await authenticate_user(email, password)
    token = await generate_access_token(user)
    return UserLoginResponse(
        token=token,
        token_type='bearer',
    )

async def logout(token: str):
    # Invalidate the token (if using a token blacklist)
    # For now, this is a placeholder since token invalidation is often handled on the client side or via a token blacklist.
    return {"message": "Successfully logged out"}

async def get_me(token: str):
    # Decode the access token
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Mã token không hợp lệ hoặc hết hạn.")

    # Fetch user details from the database
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

    return UserResponse(
        id= str(user["_id"]),
        **user
    )

async def list_users(token: str):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Mã token không hợp lệ hoặc hết hạn.")
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Chỉ ADMIN mới có quyền này.")

    users = await get_users()
    return users

async def update_user(token: str, user_update: UserUpdateRequest):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Mã token không hợp lệ hoặc hết hạn.")

    user_id = payload["id"]

    return update_user_info(user_id, user_update)

async def delete_user(token: str, user_id: str):
    await auth_admin_middleware(token)
    await delete_user_service(user_id)
    return

async def update_user_admin(token: str, user_id: str, user_update: AdminUpdateUserRequest):
    await auth_admin_middleware(token)
    return update_admin_user_info(user_id, user_update)