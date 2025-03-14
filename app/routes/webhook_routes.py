from fastapi import APIRouter, Body
from fastapi.params import Query

from app.controllers.webhook_controller import retrieve_webhook, check_transferred
from app.models.webhook_model import RetrieveWebhookBase, CheckTransaction

webhook_routes = APIRouter(redirect_slashes = False)

@webhook_routes.post("/", response_description = 'Catch payment webhook', status_code = 200, response_model = RetrieveWebhookBase)
async def webhook_handler(data: RetrieveWebhookBase):
    return await retrieve_webhook(data)

@webhook_routes.get("/", response_description = 'Check payment', status_code = 200, response_model = CheckTransaction)
async def check_successful_transaction(payment_description: str = Query(..., description = 'Payment description')):
    return await check_transferred(payment_description)