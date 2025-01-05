from fastapi import APIRouter, Header, Path

from app.controllers.customer_controller import update_customer
from app.models.customer_model import CustomerUpdate

customer_router = APIRouter()

@customer_router.put("/update-info/{customer_user_id}/from-comment/{comment_id}/", response_description="Update customer info from comment (phone, address)", status_code=200)
async def update_customer_info(
        update_data: CustomerUpdate,
        authorization: str = Header(...),
        customer_user_id: str = Path(..., description="The user id of the customer from TikTok"),
        comment_id: str = Path(..., description = "The ID of the comment containing customer information"),
):
    token = authorization.split(" ")[1]
    return await update_customer(token, customer_user_id, update_data, comment_id)