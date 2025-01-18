from app.middlewares.auth_middleware import auth_admin_middleware
from app.services.sms_service import get_all_sms_service


async def get_all_sms(token):
    await auth_admin_middleware(token)
    return await get_all_sms_service()