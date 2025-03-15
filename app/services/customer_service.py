import asyncio
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from app.config.database import comments_collection, local_customers_collection, global_customers_collection, \
    order_collection
from app.models.customer_model import CustomerUpdate, DeleteRequest, LocalCustomerModel, AddLocalCustomer
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
                        "updated_at": datetime.now(),
                    },
                    "$setOnInsert": {  # Only set this if it's a new document
                        "created_at": datetime.now()
                    },
                    "$push": {  # Append new phone numbers to the existing list
                        "phone": {"$each": phone},
                        "address": {"$each": address},
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
            # Update phone in related order
            order_collection.update_one({
                "customer_user_id": update_data_dict["customer_user_id"],
                "user_id": user_id,
                },
                {
                    "$addToSet": {
                        "phone": phone_number,
                    }
                }
            )
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
            order_collection.update_one({
                "customer_user_id": update_data_dict["customer_user_id"],
                "user_id": user_id,
            },
                {
                    "$addToSet": {
                        "address": address,
                    }
                }
            )
        # Remove the address field from update_data_dict to avoid conflicts
        del update_data_dict["address"]

    # Handle other fields (e.g., address)
    if update_data_dict:
        if "$set" not in update_operations:
            update_operations["$set"] = {}
        update_operations["$set"].update(update_data_dict)

    await update_global_customer_service({"customer_user_id": update_data_dict.get("customer_user_id")}, update_operations)
    await update_local_customer_service({"customer_user_id": update_data_dict.get("customer_user_id"), "from_live_of_tiktok_id": update_data_dict["from_live_of_tiktok_id"], "user_id": user_id}, update_operations)

async def add_local_customer_service(user_id: str, update_data: AddLocalCustomer):
    update_data_dict = update_data.model_dump(exclude_unset = True)
    inserted_customer = local_customers_collection.insert_one({"customer_user_id": update_data_dict.get("customer_user_id"),
                                           "customer_tiktok_id": update_data_dict["customer_tiktok_id"],
                                           "customer_name": update_data_dict["customer_name"],
                                           "profile_picture_url": update_data_dict["profile_picture_url"],
                                           "from_live_of_tiktok_id": update_data_dict["from_live_of_tiktok_id"],
                                           "user_id": user_id,
                                            "phone": [],
                                            "address": [],
                                           "created_at": datetime.now(),
                                           "updated_at": datetime.now()})
    customer = local_customers_collection.find_one({"_id": ObjectId(inserted_customer.inserted_id)})
    customer["id"] = str(customer.pop("_id"))
    return customer

async def get_local_customer_service(customer_user_id: str, from_live_of_tiktok_id: str):
    customer = local_customers_collection.find_one({ "customer_user_id": customer_user_id, "from_live_of_tiktok_id": from_live_of_tiktok_id })
    # Handle not found
    if not customer:
        raise HTTPException(status_code = 404, detail = "Không tìm thấy khách hàng")
    # Convert ObjectId to string for `_id`
    customer["id"] = str(customer.pop("_id"))
    return customer

async def get_global_customer_service(customer_user_id: str):
    customer = global_customers_collection.find_one({ "customer_user_id": customer_user_id })
    # Handle not found
    if not customer:
        raise HTTPException(status_code = 404, detail = "Không tìm thấy khách hàng")
    # Convert ObjectId to string for `_id`
    customer["id"] = str(customer.pop("_id"))
    return customer

async def remove_customer_elements_service(request: DeleteRequest, customer_user_id: str, from_live_of_tiktok_id: str):
    customer = local_customers_collection.find_one({"customer_user_id": customer_user_id, "from_live_of_tiktok_id": from_live_of_tiktok_id})
    if not customer:
        raise HTTPException(status_code = 404, detail = "Customer not found")

    # Get current values
    current_values = customer.get(request.field, [])
    # Remove requested elements
    updated_values = [item for item in current_values if item not in request.elements]
    # If no changes needed, return current document
    if updated_values == current_values:
        return LocalCustomerModel(
            id = str(customer["_id"]),
            customer_user_id = customer["customer_user_id"],
            customer_tiktok_id = customer["customer_tiktok_id"],
            customer_name = customer["customer_name"],
            profile_picture_url = customer["profile_picture_url"],
            user_id = customer["user_id"],
            from_live_of_tiktok_id = customer["from_live_of_tiktok_id"],
            phone = customer["phone"],
            address = customer["address"]
        )
    # Update the document
    update_result = local_customers_collection.update_one(
        {"customer_user_id": customer_user_id, "from_live_of_tiktok_id": from_live_of_tiktok_id},
        {"$set": {request.field: updated_values}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code = 500, detail = "Failed to update customer")
    # Fetch updated document
    updated_customer = local_customers_collection.find_one({"customer_user_id": customer_user_id, "from_live_of_tiktok_id": from_live_of_tiktok_id})
    return LocalCustomerModel(
        id = str(updated_customer["_id"]),
        customer_user_id = updated_customer["customer_user_id"],
        customer_tiktok_id = updated_customer["customer_tiktok_id"],
        customer_name = updated_customer["customer_name"],
        profile_picture_url = updated_customer["profile_picture_url"],
        user_id = updated_customer["user_id"],
        from_live_of_tiktok_id = updated_customer["from_live_of_tiktok_id"],
        phone = updated_customer["phone"],
        address = updated_customer["address"]
    )