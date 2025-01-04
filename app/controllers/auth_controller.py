from fastapi import HTTPException
from jose import JWTError
from app.services.auth_service import create_user, authenticate_user, generate_access_token, decode_access_token, \
    get_user_by_email, get_users, update_user_info
from app.models.user_model import User, UserResponse, UserLogin, UserLoginResponse, UserUpdateRequest


async def signup(user: User):
    new_user = await create_user(user)
    return UserResponse(
        id=new_user["_id"],
        email=new_user["email"],
        phone=new_user["phone"],
        tiktok_ids=new_user.get("tiktok_ids", []),
        role=new_user["role"],
        paid=new_user["paid"],
        verified=new_user["verified"]
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
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Fetch user details from the database
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id= str(user["_id"]),
        email= user["email"],
        phone= user["phone"],
        tiktok_ids= user["tiktok_ids"],
        role= user["role"],
        paid= user["paid"],
        verified= user["verified"]
    )

async def list_users(token: str):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")

    users = get_users()
    return users

async def update_user(token: str, user_update: UserUpdateRequest):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload["id"]

    return update_user_info(user_id, user_update)