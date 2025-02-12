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

                global_customer_data = {
                    "customer_user_id": customer_user_id,
                    "customer_tiktok_id": comment["customer_tiktok_id"],
                    "customer_name": comment["customer_name"],
                    "profile_picture_url": comment["profile_picture_url"],
                    "phone": [],
                    "address": [],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                }
                try:
                    global_customers_collection.insert_one(global_customer_data)
                except DuplicateKeyError:
                    global_customer = global_customers_collection.find_one({"customer_user_id": customer_user_id})
                    phone = global_customer["phone"]
                    address = global_customer["address"]

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

    # Handle other fields (e.g., address)
    if update_data_dict:
        if "$set" not in update_operations:
            update_operations["$set"] = {}
        update_operations["$set"].update(update_data_dict)

    await update_global_customer_service({"customer_user_id": update_data_dict.get("customer_user_id")}, update_operations)
    await update_local_customer_service({"customer_user_id": update_data_dict.get("customer_user_id"), "user_id": user_id}, update_operations)