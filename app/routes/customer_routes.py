from fastapi import APIRouter, Header, Path, Query

from app.controllers.customer_controller import update_customer, get_local_customer, get_global_customer, \
    remove_customer_elements
from app.models.customer_model import CustomerUpdate, LocalCustomerModel, GlobalCustomerModel, DeleteRequest

customer_router = APIRouter()

@customer_router.put("/update-info", response_description="Update customer info from comment (phone, address)", status_code=200)
async def update_customer_info(update_data: CustomerUpdate, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await update_customer(token, update_data)

@customer_router.get("/local", response_model=LocalCustomerModel, response_description="Get local customer info", status_code=200)
async def get_local_customer_route(
    customer_user_id: str = Query(..., description="Customer User ID"),
    from_live_of_tiktok_id: str = Query(..., description="Tiktok Live ID"),
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    return await get_local_customer(token, customer_user_id, from_live_of_tiktok_id)

@customer_router.get("/global", response_model=GlobalCustomerModel, response_description="Get global customer info", status_code=200)
async def get_global_customer_route(
    customer_user_id: str = Query(..., description="Customer User ID"),
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    return await get_global_customer(token, customer_user_id)

@customer_router.put("/local-customers/{customer_user_id}/{from_live_of_tiktok_id}/remove-elements",
         response_model=LocalCustomerModel,
         response_description="Updated customer with removed elements (phone/address)")
async def remove_elements(
    customer_user_id: str,
    from_live_of_tiktok_id: str,
    request: DeleteRequest,
    authorization: str = Header(...)
):
    token = authorization.split(" ")[1]
    return await remove_customer_elements(token, request, customer_user_id, from_live_of_tiktok_id)