from bson import ObjectId
from fastapi import HTTPException

from app.config.database import banks_collection
from app.models.bank_model import CreateBankModel, BankModel


async def create_bank_service(bank: CreateBankModel):
    bank_dict = bank.model_dump()
    new_bank = banks_collection.insert_one(bank_dict)
    bank_dict['id'] = str(new_bank.inserted_id)
    return bank_dict

async def list_bank_service():
    """
    Retrieves all bank documents from the collection, transforms the '_id' field to 'id',
    and returns the result as a list of dictionaries.
    """
    banks = banks_collection.find().to_list(length=None)  # Convert cursor to a list
    for bank in banks:
        bank['_id'] = str(bank['_id'])  # Convert ObjectId to string
        bank['id'] = bank.pop('_id')  # Rename '_id' to 'id'
    return banks

async def update_bank_service(bank_id: str, values: BankModel):
    update_data = {k: v for k, v in values.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code = 400, detail = "No fields to update provided")
    banks_collection.find_one_and_update({ "_id": ObjectId(bank_id) }, { "$set": update_data })
    updated_bank = banks_collection.find_one({ "_id": ObjectId(bank_id) })
    updated_bank['id'] = str(updated_bank.get("_id"))
    return updated_bank

async def delete_bank_service(bank_id: str):
    banks_collection.delete_one({"_id": ObjectId(bank_id)})
    return None