from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException

from app.config.database import users_collection
from app.models.user_model import User, get_password_hash, verify_password, create_access_token, decode_token, \
    UserResponse, UserUpdateRequest, UserSignUp, AdminUpdateUserRequest


async def create_user(user: dict):
    # Check if email or username already exists
    if users_collection.find_one({"email": user.get("email")}):
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash the password
    hashed_password = get_password_hash(user.get("password"))
    user.update({
        "password": hashed_password,
        "role": "user",
        "subscription_expired_at": user.get("subscription_expired_at") if user.get("subscription_expired_at") else datetime.now(),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })

    # Insert into database
    result = users_collection.insert_one(user)
    user.update({"_id": str(result.inserted_id)})
    return user

async def authenticate_user(email: str, password: str):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Verify password
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")

    return user

async def generate_access_token(user: dict):
    token_data = {
        "id": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    }
    return create_access_token(token_data)

def decode_access_token(token: str):
    return decode_token(token)

def get_user_by_email(email: str):
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_users():
    users = users_collection.find()
    user_list = [
        UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            phone=user["phone"],
            tiktok_ids=user["tiktok_ids"],
            role=user["role"],
            subscription_expired_at = user["subscription_expired_at"],
            created_at = user["created_at"],
    )
        for user in users
    ]

    return user_list

def update_user_info(user_id: str, user_update: UserUpdateRequest):
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update provided")

    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
    if updated_user:
        return UserResponse(
            id=str(updated_user["_id"]),
            email=updated_user["email"],
            phone=updated_user["phone"],
            tiktok_ids=updated_user["tiktok_ids"],
            role=updated_user["role"],
            subscription_expired_at=updated_user["subscription_expired_at"],
            created_at=updated_user["created_at"],
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")

def update_admin_user_info(user_id: str, user_update: AdminUpdateUserRequest):
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update provided")

    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
    if updated_user:
        return UserResponse(
            id=str(updated_user["_id"]),
            email=updated_user["email"],
            phone=updated_user["phone"],
            tiktok_ids=updated_user["tiktok_ids"],
            role=updated_user["role"],
            subscription_expired_at=updated_user["subscription_expired_at"],
            created_at=updated_user["created_at"],
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")

async def delete_user_service(user_id: str):
    return users_collection.delete_one({"_id": ObjectId(user_id)})