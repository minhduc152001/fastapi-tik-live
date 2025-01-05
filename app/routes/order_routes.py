from typing import List

from fastapi import APIRouter, Header, Path

from app.controllers.order_controller import create_order, get_order, get_orders
from app.models.order_model import Order, OrderDetail

order_router = APIRouter()

@order_router.post("/", response_description = "Create Order", status_code = 201, response_model=Order)
async def add_order(order: Order, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await create_order(token, order)

@order_router.get("/{order_id}", response_description = "Get Order", status_code = 200, response_model = OrderDetail)
async def retrieve_order(order_id: str = Path(..., description = "Order ID"), authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await get_order(token, order_id)

@order_router.get('/', response_description = "List all Orders", status_code = 200, response_model = List[OrderDetail])
async def retrieve_all_orders(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await get_orders(token)
