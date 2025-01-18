from typing import List
from fastapi import APIRouter, Header
from app.controllers.qr_controller import create_qr_code, list_qr_codes
from app.models.qr_model import QRResponse, QRRequest, QRModel

qr_router=APIRouter()

@qr_router.post("/", response_description = "Create QR Code for payment", status_code = 201, response_model = QRResponse)
async def retrieve_qr_code(details: QRRequest, authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await create_qr_code(token, details)

@qr_router.get("/", response_description = "ADMINS ONLY: List QR Codes", status_code = 200, response_model = List[QRModel], tags = ["admin"])
async def list_qr_code_route(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await list_qr_codes(token)