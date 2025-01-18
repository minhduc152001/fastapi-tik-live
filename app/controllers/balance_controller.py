from app.middlewares.auth_middleware import auth_admin_middleware
from app.services.balance_service import list_balances_service


async def get_all_balances(token):
    await auth_admin_middleware(token)
    return await list_balances_service()