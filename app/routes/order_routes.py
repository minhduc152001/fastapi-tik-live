from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Header, Path
from fastapi.params import Query

from app.controllers.order_controller import create_order, get_order, get_orders
from app.models.order_model import Order, SubOrder, OrderCreateRequest

order_router = APIRouter()

@order_router.post("/", response_description = "Create Order", status_code = 201, response_model=Order)
async def add_order(order_request: OrderCreateRequest, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await create_order(token, order_request)

@order_router.get("/{order_id}", response_description = "Get Order", status_code = 200, response_model = Order)
async def retrieve_order(order_id: str = Path(..., description = "Order ID"), authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await get_order(token, order_id)

@order_router.get('/', response_description = "List all Orders", status_code = 200, response_model=List[Order])
async def retrieve_all_orders(authorization: str = Header(...), room_id: Optional[str] = Query(None),
                              customer_name: Optional[str] = Query(None),
                              start_date: Optional[datetime] = Query(None),
                              end_date: Optional[datetime] = Query(None),
                              customer_user_id: Optional[str] = Query(None)):
    token = authorization.split(" ")[1]
    filters = {}
    if room_id:
        filters["room_id"] = room_id
    if customer_user_id:
        filters["customer_user_id"] = customer_user_id
    if customer_name:
        filters["customer_name"] = {"$regex": customer_name, "$options": "i"}  # Case-insensitive search
    if start_date and end_date:
        filters["created_at"] = {"$gte": start_date, "$lte": end_date}
    return await get_orders(token, filters)
