from datetime import datetime, timedelta

from bson import ObjectId
from fastapi import HTTPException

from app.config.database import users_collection
from app.models.user_model import User, get_password_hash, verify_password, create_access_token, decode_token, \
    UserResponse, UserUpdateRequest, UserSignUp, AdminUpdateUserRequest


async def create_user(user: dict):
    # Check if email or username already exists
    if users_collection.find_one({"email": user.get("email")}):
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

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
        raise HTTPException(status_code=400, detail="Không tìm thấy người dùng.")

    # Verify password
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=400, detail="Sai mật khẩu.")

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
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
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
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code = 404, detail = "Không tìm thấy người dùng.")

    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code = 400, detail = "Hãy gửi thông tin cần cập nhật.")

    # Handle TikTok IDs update
    if "tiktok_ids" in update_data:
        current_tiktok_ids = user.get("tiktok_ids", [])
        new_tiktok_ids = update_data["tiktok_ids"]
        last_updated = user.get("last_tiktok_ids_updated_at")
        max_slots = user.get("max_tiktok_id_slots", 3)

        # Check array size against max slots
        if len(new_tiktok_ids) > max_slots:
            raise HTTPException(status_code = 403, detail = f"Vượt quá giới hạn số lượng TikTok ID ({max_slots})")

        # Check global uniqueness
        for tiktok_id in new_tiktok_ids:
            if tiktok_id:  # Skip empty strings if any
                existing_user = users_collection.find_one({"tiktok_ids": tiktok_id})
                if existing_user and str(existing_user["_id"]) != user_id:
                    raise HTTPException(status_code = 409,
                                        detail = f"TikTok ID '{tiktok_id}' đã được sử dụng bởi người dùng khác"
                                        )

        # Analyze changes
        old_set = set(current_tiktok_ids)
        new_set = set(new_tiktok_ids)
        added = new_set - old_set
        removed = old_set - new_set
        common = old_set | new_set

        # Check for updates (modifications to existing IDs)
        updates = 0
        for i, (old_id, new_id) in enumerate(zip(current_tiktok_ids, new_tiktok_ids)):
            print(f"old_id, new_id: {old_id}, {new_id}")
            if old_id in common and new_id in common and old_id != new_id:
                updates += 1

        # Apply 3-day rule
        is_within_3_days = last_updated and (datetime.now() - last_updated) < timedelta(days = 3)
        if is_within_3_days and updates > 0:
            raise HTTPException(status_code = 403,
                                detail = "Không thể cập nhật TikTok ID trong vòng 3 ngày"
                                )

        # After 3 days, allow only one update
        if not is_within_3_days and updates > 1:
            raise HTTPException(status_code = 403, detail = "Chỉ một TikTOK ID được cập nhật cùng lúc")

        # Update last_tiktok_ids_updated_at only for updates, not adds/removes
        if updates > 0:
            update_data["last_tiktok_ids_updated_at"] = datetime.now()
        elif added or removed:
            # Ensure last_tiktok_ids_updated_at isn't updated for adds/removes
            if "last_tiktok_ids_updated_at" in update_data:
                del update_data["last_tiktok_ids_updated_at"]

    # Perform the update
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    # Fetch and return updated user
    updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
    if updated_user:
        return UserResponse(
            id = str(updated_user["_id"]),
            email = updated_user["email"],
            phone = updated_user["phone"],
            tiktok_ids = updated_user["tiktok_ids"],
            role = updated_user["role"],
            subscription_expired_at = updated_user.get("subscription_expired_at"),
            created_at = updated_user["created_at"],
            last_tiktok_ids_updated_at = updated_user.get("last_tiktok_ids_updated_at"),
            max_tiktok_id_slots = updated_user.get("max_tiktok_id_slots", 3)
        )
    else:
        raise HTTPException(status_code = 404, detail = "Không tìm thấy người dùng.")

def update_admin_user_info(user_id: str, user_update: AdminUpdateUserRequest):
    update_data = {k: v for k, v in user_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Hãy cung cấp thông tin cần cập nhật")

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
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")

async def delete_user_service(user_id: str):
    return users_collection.delete_one({"_id": ObjectId(user_id)})