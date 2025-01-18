from typing import List

from fastapi import APIRouter, Header

from app.controllers.balance_controller import get_all_balances
from app.models.balance_model import BalanceMovementBase

balance_router = APIRouter()

@balance_router.get('/', response_description = 'ADMINS ONLY: Get all balance movements', status_code = 200, response_model = List[BalanceMovementBase])
async def list_balances_route(authorization: str = Header(...)):
    token = authorization.split(' ')[1]
    return await get_all_balances(token)