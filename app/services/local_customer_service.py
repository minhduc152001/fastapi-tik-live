from fastapi import HTTPException
from app.config.database import local_customers_collection

async def update_local_customer_service(condition: dict, update_data: dict):
    local_customers_collection.update_many(condition, update_data, upsert = True)
    return []