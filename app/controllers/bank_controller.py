from app.middlewares.auth_middleware import auth_admin_middleware, auth_middleware
from app.models.bank_model import CreateBankModel, BankModel
from app.services.bank_service import create_bank_service, list_bank_service, delete_bank_service, update_bank_service


async def create_bank(token: str, data: CreateBankModel):
    await auth_admin_middleware(token=token)
    return await create_bank_service(data)

async def list_banks(token: str):
    await auth_middleware(token=token)
    return await list_bank_service()

async def delete_bank(token: str, bank_id: str):
    await auth_admin_middleware(token=token)
    return await delete_bank_service(bank_id)

async def update_bank(token, bank_id: str, values: BankModel):
    await auth_admin_middleware(token=token)
    return await update_bank_service(bank_id, values)