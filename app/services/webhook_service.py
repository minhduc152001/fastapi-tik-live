from datetime import datetime
from datetime import timedelta
from bson import ObjectId
from fastapi import HTTPException

from app.config.database import balance_movements_collection, invoices_collection, qr_collection, users_collection, \
    sms_collection
from app.models.webhook_model import RetrieveWebhookBase

import re

def extract_account_number(bank_code: str, msg: str) -> str:
    match = ''
    if bank_code == "VCB":
        # VCB: Account number is the first numeric sequence
        match = re.search(r"TK (\d+)", msg)
    elif bank_code == "ACB":
        # ACB: Account number is after "TK "
        match = re.search(r"TK (\d+)", msg)
    return match.group(1) if match else None

def extract_amount(bank_code: str, msg: str) -> str:
    """
    Extracts the transaction amount, including the sign (+ or -).

    Args:
        bank_code (str): The bank code (e.g., "VCB" or "ACB").
        msg (str): The transaction message.

    Returns:
        str: The amount with the sign (+ or -).
    """
    if bank_code == "VCB":
        # VCB: Match "+<number>" or "-<number>"
        match = re.search(r"([+-][\d,]+)VND", msg)
    elif bank_code == "ACB":
        # ACB: Match "+ <number>" or "- <number>" and remove the space
        match = re.search(r"([+-]) ?([\d,]+)", msg)
        if match:
            return int(match.group(1) + match.group(2).replace(",", ""))
    return int(match.group(1).replace(",", "")) if match else None

def extract_transfer_time(bank_code: str, msg: str) -> datetime:
    match = ''
    time_format = ''
    if bank_code == "VCB":
        # VCB: Time is after "luc"
        match = re.search(r"luc (\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})", msg)
        time_format = "%d-%m-%Y %H:%M:%S"
    elif bank_code == "ACB":
        # ACB: Time is "HH:MM DD/MM/YYYY"
        match = re.search(r"luc (\d{2}:\d{2} \d{2}/\d{2}/\d{4})", msg)
        time_format = "%H:%M %d/%m/%Y"
    return datetime.strptime(match.group(1), time_format) if match else None

def extract_current_balance(bank_code: str, msg: str) -> int:
    match = ''
    if bank_code == "VCB":
        # VCB: Current balance is after "SD "
        match = re.search(r"SD (\d{1,3}(,\d{3})*)VND", msg)
    elif bank_code == "ACB":
        # ACB: Current balance is after "So du"
        match = re.search(r"So du (\d{1,3}(,\d{3})*)", msg)
    return int(match.group(1).replace(",", "")) if match else None

def extract_payment_description(bank_code: str, msg: str) -> str:
    match = ''
    if bank_code == "VCB":
        # VCB: Description is after "Ref"
        match = re.search(r"Ref (.+)", msg)
    elif bank_code == "ACB":
        # ACB: Description is after "GD: "
        match = re.search(r"GD: (.+)", msg)
    return match.group(1).strip() if match else None

def parse_transaction(bank_code: str, msg: str) -> dict:
    return {
        "account_number": extract_account_number(bank_code, msg),
        "amount": extract_amount(bank_code, msg),
        "transaction_time": extract_transfer_time(bank_code, msg),  # Changed name from transfered_at
        "current_balance": extract_current_balance(bank_code, msg),
        "payment_description": extract_payment_description(bank_code, msg),
    }

def extract_invoice_id(msg: str) -> str:
    """
    Extracts the invoice ID in the format 'HoaDon<unique_alphanumeric>' from the message.

    Args:
        msg (str): The transaction message.

    Returns:
        str: The extracted invoice ID or None if not found.
    """
    # Match the pattern 'HoaDon' followed by alphanumeric characters
    match = re.search(r"HoaDon\w+", msg)
    return match.group(0) if match else None

async def handle_webhook_service(data: RetrieveWebhookBase):
    bank_code = data.sender

    # Store sms history
    try:
        sms_collection.insert_one(data.model_dump())
    except Exception as e:
        pass
        print(f"Failed to insert sms data: {e}")
        return

    if bank_code == 'Vietcombank':
        bank_code = 'VCB'
    msg = data.msg
    transaction = parse_transaction(bank_code, msg)

    # If format HoaDon___ not existed -> throw e
    if "HoaDon" not in msg:
        print(f"The description does not contain HoaDon: {bank_code} - {msg}.")
        return

    # Store balance changes
    balance_movements_collection.insert_one(transaction)

    invoice_id = extract_invoice_id(msg)
    qr = qr_collection.find_one({"payment_description": invoice_id})
    if not qr:
        print("No payment description found for invoice id: {}".format(invoice_id))
        return

    # Store invoice
    update_fields = {}
    # Handle subscription_expired_at
    month_usage = qr.get("total_months")
    user = users_collection.find_one({"_id": ObjectId(qr.get("user_id"))})

    # Handle total_tiktok_ids
    additional_tiktok_ids = qr.get("total_tiktok_ids")
    if user:
        current_slots = user.get("max_tiktok_id_slots", 0)  # Default to 5 if missing
        new_slots = current_slots + additional_tiktok_ids
        update_fields["max_tiktok_id_slots"] = new_slots
        if current_slots == 0:
            update_fields["subscription_expired_at"] = datetime.now() + timedelta(days = 30 * month_usage)
        else:
            update_fields["subscription_expired_at"] = user.get("subscription_expired_at") + timedelta(days = 30 * month_usage)
    else:
        print(f"No user found for invoice id: {invoice_id}")

    # Perform update only if there are fields to update
    users_collection.find_one_and_update({"_id": ObjectId(qr.get("user_id"))}, {"$set": update_fields})
    if not user:
        raise Exception("No user found for user id: {}".format(qr.get("user_id")))
    invoices_collection.insert_one({
        "invoice_id": invoice_id,
        "customer": user.get("email"),
        "vendor": "tatech",
        "total_months": month_usage,
        "total_month_cost": qr.get("total_month_cost"),
        "total_tiktok_ids": qr.get("total_tiktok_ids"),
        "total_amount": qr.get("total_amount"),
        "VAT": "0%",
        "created_at": datetime.now(),
    })
    user.update({"_id": ObjectId(qr.get("user_id"))})

    return data

async def check_transferred_service(payment_description: str):
    balance_details = balance_movements_collection.find_one({
        "payment_description": {"$regex": payment_description, "$options": "i"}
    })
    transferred = True
    if not balance_details:
        transferred = False
    return {
        "transferred": transferred,
    }