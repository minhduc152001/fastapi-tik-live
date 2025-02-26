import asyncio
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from app.config.database import comments_collection, local_customers_collection, global_customers_collection
from app.models.customer_model import CustomerUpdate
from app.services.global_customer_service import update_global_customer_service
from app.services.local_customer_service import update_local_customer_service


async def process_pending_customers():
    while True:
        try:
            pending_comments = comments_collection.find({"check_store_customer": False}).to_list(length=None)
            for comment in pending_comments:
                phone = []
                address = []
                customer_user_id = comment["customer_user_id"]

                local_customer_data = {
                    "customer_user_id": customer_user_id,
                    "customer_tiktok_id": comment["customer_tiktok_id"],
                    "customer_name": comment["customer_name"],
                    "profile_picture_url": comment["profile_picture_url"],
                    "user_id": comment["user_id"],
                    "from_live_of_tiktok_id": comment["from_live_of_tiktok_id"],
                    "phone": phone,
                    "address": address,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                }
                try:
                    local_customers_collection.insert_one(local_customer_data)
                except DuplicateKeyError:
                    local_customer = local_customers_collection.find_one({"customer_user_id": customer_user_id, "from_live_of_tiktok_id": comment["from_live_of_tiktok_id"]})
                    # ✅ Ensure local_customer is not None before accessing fields
                    if local_customer:
                        phone = local_customer.get("phone", [])  # Use .get() with a default empty list
                        address = local_customer.get("address", [])

                # Update global query
                update_query = {
                    "$set": {
                        "customer_tiktok_id": comment["customer_tiktok_id"],
                        "customer_name": comment["customer_name"],
                        "profile_picture_url": comment["profile_picture_url"],
                        "address": address,
                        "updated_at": datetime.now(),
                    },
                    "$setOnInsert": {  # Only set this if it's a new document
                        "created_at": datetime.now()
                    },
                    "$push": {  # Append new phone numbers to the existing list
                        "phone": {"$each": phone}
                    }
                }
                # Perform the upsert
                try:
                    global_customers_collection.update_one(
                        {"customer_user_id": customer_user_id},
                        update_query,
                        upsert = True
                    )
                except DuplicateKeyError:
                    pass

                comments_collection.update_one({"_id": comment["_id"]}, {"$set": {"check_store_customer": True}})

        except Exception as e:
            print(f"Error processing pending customers: {e}")
        await asyncio.sleep(600)  # Sleep for 10 minutes (600 seconds)

async def update_customer_service(user_id: str, update_data: CustomerUpdate):
    update_data_dict = update_data.model_dump(exclude_unset = True)
    # Initialize the update operations dictionary
    update_operations = {}

    # Handle phone field
    if "phone" in update_data_dict:
        phone_number = update_data_dict["phone"]
        if phone_number is None:
            # Set phone to an empty array
            update_operations["$set"] = {"phone": []}
        else:
            # Add phone number to the array if it doesn't exist
            update_operations["$addToSet"] = {"phone": phone_number}
        # Remove the phone field from update_data_dict to avoid conflicts
        del update_data_dict["phone"]

    # Handle address field
    if "address" in update_data_dict:
        address = update_data_dict["address"]
        if address is None:
            # Set address to an empty array
            update_operations["$set"] = {"address": []}
        else:
            # Add address to the array if it doesn't exist
            update_operations["$addToSet"] = {"address": address}
        # Remove the address field from update_data_dict to avoid conflicts
        del update_data_dict["address"]

    # Handle other fields (e.g., address)
    if update_data_dict:
        if "$set" not in update_operations:
            update_operations["$set"] = {}
        update_operations["$set"].update(update_data_dict)

    await update_global_customer_service({"customer_user_id": update_data_dict.get("customer_user_id")}, update_operations)
    await update_local_customer_service({"customer_user_id": update_data_dict.get("customer_user_id"), "user_id": user_id}, update_operations)

async def get_local_customer_service(customer_user_id: str, from_live_of_tiktok_id: str):
    customer = local_customers_collection.find_one({ "customer_user_id": customer_user_id, "from_live_of_tiktok_id": from_live_of_tiktok_id })
    # Handle not found
    if not customer:
        raise HTTPException(status_code = 404, detail = "Customer not found")
    # Convert ObjectId to string for `_id`
    customer["id"] = str(customer.pop("_id"))
    return customer

async def get_global_customer_service(customer_user_id: str):
    customer = global_customers_collection.find_one({ "customer_user_id": customer_user_id })
    # Handle not found
    if not customer:
        raise HTTPException(status_code = 404, detail = "Customer not found")
    # Convert ObjectId to string for `_id`
    customer["id"] = str(customer.pop("_id"))
    return customer
