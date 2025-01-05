from app.middlewares.auth_middleware import auth_middleware
from app.models.order_model import Order
from app.services.order_service import create_order_service, get_all_order_service, get_order_service


async def create_order(token: str, data: Order):
    await auth_middleware(token=token)
    return await create_order_service(data)

async def get_orders(token: str):
    await auth_middleware(token = token)
    return await get_all_order_service()

async def get_order(token: str, order_id: str):
    await auth_middleware(token = token)
    return await get_order_service(order_id)