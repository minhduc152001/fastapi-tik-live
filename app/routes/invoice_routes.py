from typing import List

from fastapi import APIRouter, Header

from app.controllers.invoice_controller import list_invoices
from app.models.invoice_model import InvoiceModel

invoice_router = APIRouter()

@invoice_router.get('/', response_description = "ADMINS ONLY: List all invoices", status_code = 200, response_model = List[InvoiceModel])
async def list_invoices_route(authorization: str = Header(...)):
    token = authorization.split(' ')[1]
    return await list_invoices(token)