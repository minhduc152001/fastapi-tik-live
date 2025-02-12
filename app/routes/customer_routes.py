from fastapi import APIRouter, Header, Path

from app.controllers.customer_controller import update_customer
from app.models.customer_model import CustomerUpdate

customer_router = APIRouter()

@customer_router.put("/update-info", response_description="Update customer info from comment (phone, address)", status_code=200)
async def update_customer_info(update_data: CustomerUpdate, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await update_customer(token, update_data)