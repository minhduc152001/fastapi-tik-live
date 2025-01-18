from app.middlewares.auth_middleware import auth_middleware, auth_admin_middleware
from app.models.qr_model import QRRequest
from app.services.qr_service import create_qr_code_service, list_qr_codes_service


async def create_qr_code(token: str, transfer_details: QRRequest):
    user = await auth_middleware(token)
    user_id = str(user.get('_id'))
    return await create_qr_code_service(user_id, transfer_details)

async def list_qr_codes(token: str):
    await auth_admin_middleware(token)
    return await list_qr_codes_service()