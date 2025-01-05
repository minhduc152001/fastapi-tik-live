from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from fastapi import HTTPException
from app.config.database import order_collection, global_customers_collection
from app.models.order_model import Order


async def create_order_service(order: Order):
    order_dict = order.model_dump()
    order_dict["created_at"] = datetime.now()
    order_collection.insert_one(order_dict)
    return order

async def get_order_service(order_id: str):
    order = order_collection.find_one({'_id': ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    customer = global_customers_collection.find_one({'customer_user_id': order['customer_user_id']})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "id": order_id,
        "room_id": order['room_id'],
        "from_live_of_tiktok_id": order['from_live_of_tiktok_id'],
        "customer_user_id": order['customer_user_id'],
        "customer_name": customer['customer_name'],
        "phone": customer['phone'],
        "address": customer['address'],
        "created_at": order['created_at'],
    }

async def get_all_order_service(condition: Optional[dict] = None) -> List[dict]:
    try:
        if condition is None:
            orders = order_collection.find()
        else:
            orders = order_collection.find(condition)
        order_list: List[dict] = []
        for order in orders:
            try:
                order_data = await get_order_service(str(order["_id"])) #Convert ObjectId to string
                order_list.append(order_data)
            except HTTPException as e:
                print(f"Order with id {str(order['_id'])} not found: {e.detail}")
                continue # Skip to the next order
        return order_list
    except Exception as e:
        print(f"Error listing orders: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving orders")