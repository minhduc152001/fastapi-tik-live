from fastapi import HTTPException

from app.config.database import global_customers_collection

async def update_global_customer_service(condition: dict, update_data: dict):
    global_customers_collection.update_one(condition, update_data, upsert = True)
    return []