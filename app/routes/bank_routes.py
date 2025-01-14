from typing import List

from fastapi import APIRouter, Header, Body, Path
from app.controllers.bank_controller import list_banks, create_bank, update_bank, delete_bank
from app.models.bank_model import CreateBankModel, BankDetailsModel, BankModel

bank_routes = APIRouter()

@bank_routes.get("/", response_description = 'List all banks', status_code = 200, response_model = List[BankDetailsModel])
async def get_all_banks(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return await list_banks(token)

@bank_routes.post("/", response_description = 'Create bank', status_code = 201, response_model = BankDetailsModel)
async def add_bank(authorization: str = Header(...), data: CreateBankModel = Body(...)):
    token = authorization.split(" ")[1]
    return await create_bank(token, data)

@bank_routes.put("/{bank_id}", response_description = 'Update bank', status_code = 200, response_model = BankDetailsModel)
async def get_bank(authorization: str = Header(...), bank_id: str = Path(...), data: BankModel = Body(...)):
    token = authorization.split(" ")[1]
    return await update_bank(token, bank_id, data)

@bank_routes.delete("/{bank_id}", response_description = 'Delete bank', status_code = 200)
async def remove_bank(authorization: str = Header(...), bank_id: str = Path(...)):
    token = authorization.split(" ")[1]
    return await delete_bank(token, bank_id)