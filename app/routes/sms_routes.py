from typing import List

from fastapi import APIRouter, Header

from app.controllers.sms_controller import get_all_sms
from app.models.sms_model import SMSResponse

sms_router = APIRouter()

@sms_router.get('/', response_description = 'ADMINS ONLY: Get all SMS messages', status_code = 200, response_model = List[SMSResponse])
async def list_sms_route(authorization: str = Header(...)):
    token = authorization.split(' ')[1]
    return await get_all_sms(token)