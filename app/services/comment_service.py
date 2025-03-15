from typing import List, Optional

import pymongo
from pymongo.errors import DuplicateKeyError

from app.config.database import comments_collection, global_customers_collection, local_customers_collection
from app.models.comment_model import Comment, CommentResponse


async def create_comment_service(comment: Comment) -> CommentResponse:
    try:
        comment_dict = comment.model_dump()
        new_comment = comments_collection.insert_one(comment_dict)
        comment_id = str(new_comment.inserted_id)
        comment_dict["id"] = comment_id
        return CommentResponse(**comment_dict)
    except DuplicateKeyError:
        existing_comment = comments_collection.find_one({
            "msg_id": comment.msg_id,
            "user_id": comment.user_id,
        })
        if existing_comment:
            existing_comment["id"] = str(existing_comment["_id"])
            return CommentResponse(**existing_comment)

async def list_comments_by_room_id(room_id: str,
    customer_user_id: Optional[str] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None
) -> List[CommentResponse]:
    query = {"room_id": room_id}
    if customer_user_id:
        query["customer_user_id"] = customer_user_id

    cursor = comments_collection.find(query).sort("_id", pymongo.DESCENDING)

    # Apply skip if provided
    if skip is not None:
        cursor = cursor.skip(skip)

    # Apply limit if provided
    if limit is not None:
        cursor = cursor.limit(limit)

    comment_list = []
    for comment in cursor:
        # Get customer data for phone checks
        global_customer = global_customers_collection.find_one({"customer_user_id": comment["customer_user_id"]})
        local_customer = local_customers_collection.find_one({
            "customer_user_id": comment["customer_user_id"],
            "from_live_of_tiktok_id": comment["from_live_of_tiktok_id"]
        })

        # Prepare comment data with new fields
        comment_data = {
            "id": str(comment["_id"]),
            "room_id": comment["room_id"],
            "user_id": comment["user_id"],
            "msg_id": comment["msg_id"],
            "from_live_of_tiktok_id": comment["from_live_of_tiktok_id"],
            "customer_user_id": comment["customer_user_id"],
            "customer_tiktok_id": comment["customer_tiktok_id"],
            "customer_name": comment["customer_name"],
            "comment": comment["comment"],
            "profile_picture_url": comment["profile_picture_url"],
            "check_store_customer": comment["check_store_customer"],
            "created_at": comment["created_at"],
            "has_global_phone": bool(
                global_customer and global_customer.get("phone") and len(global_customer["phone"]) > 0
                ),
            "has_local_phone": bool(local_customer and local_customer.get("phone") and len(local_customer["phone"]) > 0)
        }

        comment_list.append(CommentResponse(**comment_data))

    return comment_list