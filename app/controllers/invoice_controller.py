from app.middlewares.auth_middleware import auth_admin_middleware
from app.services.invoice_service import list_invoices_service


async def list_invoices(token):
    await auth_admin_middleware(token)
    return await list_invoices_service()