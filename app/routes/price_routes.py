from typing import List

from fastapi import APIRouter, Header, Body, Path

from app.controllers.price_controller import list_prices, create_price, update_price, delete_price
from app.models.price_model import PriceModel, PriceRequest

price_router = APIRouter()

@price_router.get("/", response_description = "List pricing", status_code = 200, response_model = List[PriceModel])
async def get_prices_route(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await list_prices(token)

@price_router.post("/", response_description = "ADMINS ONLY: Create new price", status_code = 201, response_model = PriceModel)
async def create_price_route(authorization: str = Header(...), data: PriceRequest = Body(...)):
    token = authorization.split(" ")[1]
    return await create_price(token, data)

@price_router.put("/{price_id}", response_description = "ADMINS ONLY: Update pricing", status_code = 200, response_model = PriceModel)
async def update_price_route(authorization: str = Header(...), data: PriceRequest = Body(...), price_id: str = Path(...)):
    token = authorization.split(" ")[1]
    return await update_price(token, price_id, data)

@price_router.delete("/{price_id}", response_description = "ADMINS ONLY: Delete pricing", status_code = 204)
async def delete_price_route(authorization: str = Header(...), price_id: str = Path(...)):
    token = authorization.split(" ")[1]
    return await delete_price(token, price_id)