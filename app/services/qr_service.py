from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException

from app.config.database import qr_collection
from app.constant.enum import bank_names
from app.models.qr_model import QRRequest, QRResponse


async def create_qr_code_service(user_id: str, details: QRRequest):
    details_dict = details.model_dump()
    try:
        details_dict["bank_name"] = bank_names[details.bank_code]
    except KeyError:
        raise HTTPException(400, "No bank code")
    details_dict["user_id"] = user_id
    details_dict["payment_description"] = None
    details_dict["created_at"] = datetime.now()
    details_dict["total_amount"] = details.amount_per_month * details.subscription_months
    new_qr_id = qr_collection.insert_one(details_dict).inserted_id
    payment_description = f"HoaDon{new_qr_id}"
    qr = qr_collection.find_one_and_update({"_id": ObjectId(new_qr_id)}, {"$set": {"payment_description": payment_description}})
    return {
        "bank_name": qr.get("bank_name"),
        "payment_description": payment_description,
        "url": f"https://qr.sepay.vn/img?acc={qr.get("account_number")}&bank={qr.get("bank_code")}&amount={qr.get("total_amount")}&des={payment_description}&template=compact"
    }