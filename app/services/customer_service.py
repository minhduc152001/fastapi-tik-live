from pymongo.errors import DuplicateKeyError

from app.config.database import customers_collection
from app.models.customer_model import Customer, CustomerResponse


async def create_customer_service(customer: Customer) -> CustomerResponse:
    try:
        customer_dict = customer.model_dump()
        new_customer = customers_collection.insert_one(customer_dict)
        customer_id = str(new_customer.inserted_id)
        customer_dict["id"] = customer_id
        return CustomerResponse(**customer_dict)
    except DuplicateKeyError:
        existing_customer = customers_collection.find_one({
            "tiktok_user_id": customer.tiktok_user_id,
        })
        if existing_customer:
            existing_customer["id"] = str(existing_customer["_id"])
            return CustomerResponse(**existing_customer)