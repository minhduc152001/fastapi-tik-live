from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from fastapi import HTTPException
from app.config.database import order_collection, global_customers_collection, rooms_collection, \
    local_customers_collection
from app.models.order_model import Order, SubOrder, OrderCreateRequest


def format_order(order_dict):
    order_dict["id"] = str(order_dict["_id"])
    del order_dict["_id"]
    return order_dict

async def create_order_service(order_request: OrderCreateRequest, user_id: str):
    sub_order = order_request.sub_order
    room_id = order_request.room_id
    customer_user_id = order_request.customer_user_id
    from_live_of_tiktok_id = order_request.from_live_of_tiktok_id
    customer_tiktok_id = order_request.customer_tiktok_id
    customer_name = order_request.customer_name

    # Check existing order
    existing_order = order_collection.find_one({
        "room_id": room_id,
        "customer_user_id": customer_user_id
    }
    )
    # Prepare sub_order data
    sub_order_dict = sub_order.model_dump()
    # Check if msg_id already exists
    if order_collection.find_one({"sub_orders.msg_id": sub_order.msg_id}):
        updated_order = order_collection.find_one({"_id": existing_order["_id"]})
        return format_order(updated_order)
    # If order exists, append to sub_orders
    if existing_order:
        order_collection.update_one(
            {"_id": existing_order["_id"]},
            {
                "$push": {"sub_orders": sub_order_dict},
                "$set": {"updated_at": datetime.now()}
            }
        )
        updated_order = order_collection.find_one({"_id": existing_order["_id"]})
        return format_order(updated_order)
    # If no order exists, create new one
    order_dict = {
        "room_id": room_id,
        "customer_user_id": customer_user_id,
        "user_id": user_id,
        "from_live_of_tiktok_id": from_live_of_tiktok_id,
        "customer_tiktok_id": customer_tiktok_id,
        "customer_name": customer_name,
        "sub_orders": [sub_order_dict],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    # Get room details
    room = rooms_collection.find_one({"_id": ObjectId(order_dict["room_id"])})
    if not room:
        raise HTTPException(status_code = 400, detail = "Buổi phát trực tiếp này không còn")
    order_dict["live_started_at"] = room.get("created_at")
    order_dict["live_title"] = room.get("title")

    # Get phone and address from local_customers
    local_customer = local_customers_collection.find_one({
        "customer_tiktok_id": order_dict["customer_tiktok_id"],
        "from_live_of_tiktok_id": order_dict["from_live_of_tiktok_id"]
    }
    )

    if not local_customer:
        new_local_customer = {
            "customer_user_id": customer_user_id,
            "customer_tiktok_id": customer_tiktok_id,
            "customer_name": customer_name,
            "profile_picture_url": "",
            "user_id": user_id,
            "from_live_of_tiktok_id": from_live_of_tiktok_id,
            "phone": [],
            "address": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        local_customers_collection.insert_one(new_local_customer)
        order_dict["phone"] = []
        order_dict["address"] = []
    else:
        order_dict["phone"] = local_customer.get("phone", [])
        order_dict["address"] = local_customer.get("address", [])

    result = order_collection.insert_one(order_dict)
    new_order = order_collection.find_one({"_id": result.inserted_id})
    return format_order(new_order)

async def get_order_service(order_id: str, user_id: str):
    order = order_collection.find_one({'_id': ObjectId(order_id), "user_id": user_id})
    if not order:
        raise HTTPException(status_code = 404, detail = "Đơn hàng này không tồn tại")
    return format_order(order)


async def get_all_order_service(user_id: str, condition: Optional[dict] = None):
    try:
        query = condition or {}
        query["user_id"] = user_id
        cursor = order_collection.find(query)
        orders = cursor.to_list(length = None)
        formatted_orders = [format_order(order) for order in orders]
        return formatted_orders
    except Exception as e:
        print(f"Error listing orders: {e}")
        raise HTTPException(status_code = 500, detail = "Có lỗi xảy ra trong quá trình lấy dữ liệu. Hãy thử lại!")