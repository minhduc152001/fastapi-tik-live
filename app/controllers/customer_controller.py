from fastapi import HTTPException
from jose import JWTError

from app.models.customer_model import CustomerUpdate
from app.services.auth_service import decode_access_token, get_user_by_email
from app.services.customer_service import update_customer_service


async def update_customer(token: str, customer_user_id: str, update_data: CustomerUpdate, comment_id: str):
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(status_code = 401, detail = "Invalid or expired token")
    user = get_user_by_email(payload["email"])
    if not user:
        raise HTTPException(status_code = 404, detail = "User not found")
    await update_customer_service(customer_user_id, update_data, comment_id)
