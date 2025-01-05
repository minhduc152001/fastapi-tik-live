from fastapi import HTTPException

from app.config.database import global_customers_collection
from app.models.customer_model import GlobalCustomer, GlobalCustomerResponse

async def update_global_customer_service(condition: dict, update_data: dict) -> GlobalCustomerResponse:
    global_customers_collection.update_one(condition, {
        "$set": update_data,
    })
    updated_customer = global_customers_collection.find_one(condition)
    if updated_customer is None:
        raise HTTPException(status_code=404, detail="Global customer not found")
    updated_customer["id"] = str(updated_customer["_id"])
    return GlobalCustomerResponse(**updated_customer)