from typing import Optional, Dict

from app.middlewares.auth_middleware import auth_middleware
from app.models.order_model import Order
from app.services.order_service import create_order_service, get_all_order_service, get_order_service


async def create_order(token: str, data: Order):
    user = await auth_middleware(token=token)
    return await create_order_service(data, str(user.get("_id")))

async def get_orders(token: str, filters: Optional[Dict[str, str]] = None):
    user = await auth_middleware(token = token)
    return await get_all_order_service(str(user.get("_id")), filters)

async def get_order(token: str, order_id: str):
    user = await auth_middleware(token = token)
    return await get_order_service(str(user.get("_id")), order_id)