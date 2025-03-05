from fastapi import HTTPException
from jose import JWTError

from app.middlewares.auth_middleware import auth_middleware
from app.models.customer_model import CustomerUpdate, DeleteRequest
from app.services.auth_service import decode_access_token, get_user_by_email
from app.services.customer_service import update_customer_service, get_local_customer_service, \
    get_global_customer_service, remove_customer_elements_service


async def update_customer(token: str, update_data: CustomerUpdate):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code = 401, detail = "Mã token không hợp lệ hoặc hết hạn.")
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code = 404, detail = "Không tìm thấy người dùng")
    await update_customer_service(str(user.get('_id')), update_data)

async def get_local_customer(token: str, customer_user_id: str, from_live_of_tiktok_id: str):
    await auth_middleware(token = token)
    return await get_local_customer_service(customer_user_id, from_live_of_tiktok_id)

async def get_global_customer(token: str, customer_user_id: str):
    await auth_middleware(token = token)
    return await get_global_customer_service(customer_user_id)

async def remove_customer_elements(token: str, request: DeleteRequest, customer_user_id: str, from_live_of_tiktok_id: str):
    await auth_middleware(token = token)
    return await remove_customer_elements_service(request, customer_user_id, from_live_of_tiktok_id)