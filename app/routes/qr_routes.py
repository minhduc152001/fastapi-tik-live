from fastapi import APIRouter, Header

from app.controllers.qr_controller import create_qr_code
from app.models.qr_model import QRResponse, QRRequest

qr_routes=APIRouter()

@qr_routes.post("/", response_description = "Create QR Code for payment", status_code = 201, response_model = QRResponse)
async def retrieve_qr_code(details: QRRequest, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await create_qr_code(token, details)