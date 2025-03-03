from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from fastapi import HTTPException
from app.config.database import order_collection, global_customers_collection, rooms_collection, \
    local_customers_collection
from app.models.order_model import Order, OrderDetail


async def create_order_service(order: Order, user_id: str):
    # Check if msg_id already exists
    existing_order = order_collection.find_one({"msg_id": order.msg_id})
    if existing_order:
        return OrderDetail(
            id = str(existing_order["_id"]),
            room_id = existing_order["room_id"],
            msg_id = existing_order["msg_id"],
            from_live_of_tiktok_id = existing_order["from_live_of_tiktok_id"],
            customer_user_id = existing_order["customer_user_id"],
            customer_tiktok_id = existing_order["customer_tiktok_id"],
            customer_name = existing_order["customer_name"],
            comment = existing_order["comment"],
            phone = existing_order.get("phone", []),
            address = existing_order.get("address", []),
            user_id = existing_order["user_id"],
            live_title = existing_order["live_title"],
            live_started_at = existing_order["live_started_at"],
            created_at = existing_order["created_at"],
            updated_at = existing_order["updated_at"]
        )

    # If msg_id doesn't exist, proceed with creation
    order_dict = order.model_dump()
    order_dict["created_at"] = datetime.now()
    order_dict["updated_at"] = datetime.now()
    order_dict["user_id"] = user_id

    # Get room details
    room = rooms_collection.find_one({"_id": ObjectId(order_dict["room_id"])})
    if not room:
        raise HTTPException(status_code = 400, detail = "Buổi phát trực tiếp này không còn")

    # Query local_customers_collection for phone and address
    local_customer = local_customers_collection.find_one({
        "customer_tiktok_id": order_dict["customer_tiktok_id"],
        "from_live_of_tiktok_id": order_dict["from_live_of_tiktok_id"]
    }
    )

    if not local_customer:
        # Create new local customer if not existing
        new_local_customer = {
            "customer_user_id": order_dict["customer_user_id"],
            "customer_tiktok_id": order_dict["customer_tiktok_id"],
            "customer_name": order_dict["customer_name"],
            "profile_picture_url": "",  # Default empty as it's not in Order model
            "user_id": user_id,
            "from_live_of_tiktok_id": order_dict["from_live_of_tiktok_id"],
            "phone": [],  # Default empty list
            "address": [],  # Default empty list
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        local_customers_collection.insert_one(new_local_customer)
        order_dict["phone"] = []
        order_dict["address"] = []
    else:
        order_dict["phone"] = local_customer.get("phone", [])
        order_dict["address"] = local_customer.get("address", [])

    order_dict["live_started_at"] = room.get("created_at")
    order_dict["live_title"] = room.get("title")

    # Insert the new order
    inserted_order = order_collection.insert_one(order_dict)

    return OrderDetail(
        id = str(inserted_order.inserted_id),
        **order_dict
    )

async def get_order_service(order_id: str, user_id: str):
    order = order_collection.find_one({'_id': ObjectId(order_id), "user_id": user_id})
    if not order:
        raise HTTPException(status_code = 404, detail = "Đơn hàng này không tồn tại")

    return OrderDetail(
        id = str(order["_id"]),
        room_id = order["room_id"],
        msg_id = order["msg_id"],
        from_live_of_tiktok_id = order["from_live_of_tiktok_id"],
        customer_user_id = order["customer_user_id"],
        customer_tiktok_id = order["customer_tiktok_id"],
        customer_name = order["customer_name"],
        comment = order["comment"],
        phone = order.get("phone", []),
        address = order.get("address", []),
        user_id = order["user_id"],
        live_title = order["live_title"],
        live_started_at = order["live_started_at"],
        created_at = order["created_at"],
        updated_at = order["updated_at"]
    )


async def get_all_order_service(user_id: str, condition: Optional[dict] = None) -> List[OrderDetail]:
    try:
        query = condition or {}
        query["user_id"] = user_id
        cursor = order_collection.find(query)
        orders = await cursor.to_list(length = None)

        return [
            OrderDetail(
                id = str(order["_id"]),
                room_id = order["room_id"],
                msg_id = order["msg_id"],
                from_live_of_tiktok_id = order["from_live_of_tiktok_id"],
                customer_user_id = order["customer_user_id"],
                customer_tiktok_id = order["customer_tiktok_id"],
                customer_name = order["customer_name"],
                comment = order["comment"],
                phone = order.get("phone", []),
                address = order.get("address", []),
                user_id = order["user_id"],
                live_title = order["live_title"],
                live_started_at = order["live_started_at"],
                created_at = order["created_at"],
                updated_at = order["updated_at"]
            )
            for order in orders
        ]
    except Exception as e:
        print(f"Error listing orders: {e}")
        raise HTTPException(status_code = 500, detail = "Có lỗi xảy ra trong quá trình lấy dữ liệu. Hãy thử lại!")