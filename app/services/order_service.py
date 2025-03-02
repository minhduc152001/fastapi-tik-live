from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from fastapi import HTTPException
from app.config.database import order_collection, global_customers_collection, rooms_collection
from app.models.order_model import Order, OrderDetail


async def create_order_service(order: Order, user_id: str):
    order_dict = order.model_dump()
    order_dict["created_at"] = datetime.now()
    order_dict["updated_at"] = datetime.now()
    global_customer = global_customers_collection.find_one({"customer_user_id": order_dict["customer_user_id"]})
    if not global_customer:
        raise HTTPException(status_code=400, detail="Không tìm thấy khách hàng")
    room = rooms_collection.find_one({"_id": ObjectId(order_dict["room_id"])})
    if not room:
        raise HTTPException(status_code=400, detail="Buổi phát trực tiếp này không còn")
    order_dict["customer_tiktok_id"] = global_customer.get("customer_tiktok_id")
    order_dict["customer_name"] = global_customer.get("customer_name")
    order_dict["phone"] = global_customer.get("phone")
    order_dict["address"] = global_customer.get("address")
    order_dict["user_id"] = user_id
    order_dict["live_started_at"] = room.get("created_at")
    order_dict["live_title"] = room.get("title")
    order_dict["from_live_of_tiktok_id"] = room.get("tiktok_id")
    order_dict["note"] = None
    inserted_order = order_collection.insert_one(order_dict)
    new_order = OrderDetail(
        id = str(inserted_order.inserted_id),
        **order_dict
    )
    return new_order

async def get_order_service(order_id: str, user_id: str):
    order = order_collection.find_one({'_id': ObjectId(order_id), user_id: user_id})
    if not order:
        raise HTTPException(status_code=404, detail="Đơn hàng này không tồn tại")
    return OrderDetail(
        id = str(order["_id"]),
        customer_user_id = order["customer_user_id"],
        customer_tiktok_id = order["customer_tiktok_id"],
        customer_name = order["customer_name"],
        phone = order.get("phone", []),  # Default to empty list if missing
        address = order.get("address"),
        user_id = order["user_id"],
        live_started_at = order["live_started_at"],
        live_title = order["live_title"],
        from_live_of_tiktok_id = order["from_live_of_tiktok_id"],
        note = order.get("note"),
        created_at = order["created_at"],
        updated_at = order["updated_at"]
    )


async def get_all_order_service(user_id: str, condition: Optional[dict] = None) -> List[OrderDetail]:
    try:
        query = condition or {}
        query["user_id"] = user_id  # Ensure filtering by user_id
        cursor = order_collection.find(query)
        orders = cursor.to_list(length = None)  # Fetch all results
        return [
            OrderDetail(
                id = str(order["_id"]),
                customer_user_id = order["customer_user_id"],
                customer_tiktok_id = order["customer_tiktok_id"],
                customer_name = order["customer_name"],
                phone = order.get("phone", []),
                address = order.get("address"),
                user_id = order["user_id"],
                live_started_at = order["live_started_at"],
                live_title = order["live_title"],
                from_live_of_tiktok_id = order["from_live_of_tiktok_id"],
                note = order.get("note"),
                created_at = order["created_at"],
                updated_at = order["updated_at"]
            )
            for order in orders
        ]
    except Exception as e:
        print(f"Error listing orders: {e}")
        raise HTTPException(status_code=500, detail="Có lỗi xảy ra trong quá trình lấy dữ liệu. Hãy thử lại!")