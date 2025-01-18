from app.middlewares.auth_middleware import auth_admin_middleware
from app.models.price_model import PriceRequest
from app.services.price_service import list_prices_service, create_price_service, update_price_service, \
    delete_price_service


async def list_prices(token: str):
    await auth_admin_middleware(token)
    return await list_prices_service()

async def create_price(token: str, data: PriceRequest):
    await auth_admin_middleware(token)
    return await create_price_service(data)

async def update_price(token: str, price_id: str, data: PriceRequest):
    await auth_admin_middleware(token)
    return await update_price_service(price_id, data)

async def delete_price(token: str, price_id: str):
    await auth_admin_middleware(token)
    return await delete_price_service(price_id)