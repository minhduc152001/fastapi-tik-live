from fastapi import HTTPException

from app.models.webhook_model import RetrieveWebhookBase
from app.services.webhook_service import handle_webhook_service, check_transferred_service


async def retrieve_webhook(data: RetrieveWebhookBase):
    try:
        return await handle_webhook_service(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def check_transferred(payment_description: str):
    return await check_transferred_service(payment_description)