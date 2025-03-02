from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import HTTPException

from app.config.database import qr_collection, users_collection
from app.constant.enum import bank_names
from app.constant.fixedVar import PRICE_PER_TIKTOK_ID
from app.models.qr_model import QRRequest

async def create_qr_code_service(user_id: str, details: QRRequest):
    details_dict = details.model_dump()
    try:
        details_dict["bank_name"] = bank_names[details.bank_code]
    except KeyError:
        raise HTTPException(400, "No bank code")
    details_dict["user_id"] = user_id
    details_dict["payment_description"] = None
    details_dict["created_at"] = datetime.now()
    if details.total_month_cost > 0 and details.total_tiktok_ids == 1:
        details_dict["total_amount"] = details.total_month_cost
    else:
        details_dict["total_amount"] = details.total_tiktok_ids * PRICE_PER_TIKTOK_ID
    new_qr_id = qr_collection.insert_one(details_dict).inserted_id
    payment_description = f"HoaDon{new_qr_id}"
    qr = qr_collection.find_one_and_update({"_id": ObjectId(new_qr_id)}, {"$set": {"payment_description": payment_description}})
    return {
        "bank_name": qr.get("bank_name"),
        "payment_description": payment_description,
        "url": f"https://qr.sepay.vn/img?acc={qr.get("account_number")}&bank={qr.get("bank_code")}&amount={qr.get("total_amount")}&des={payment_description}&template=compact"
    }

async def list_qr_codes_service():
    qr_codes = qr_collection.find()
    qr_list: List[dict] = []
    for qr_code in qr_codes:
        qr_list.append({
            "id": str(qr_code["_id"]),
            "bank_code": qr_code["bank_code"],
            "account_number": qr_code["account_number"],
            "total_month_cost": qr_code["total_month_cost"],
            "total_months": qr_code["total_months"],
            "total_tiktok_ids": qr_code["total_tiktok_ids"],
            "bank_name": qr_code["bank_name"],
            "payment_description": qr_code["payment_description"],
            "created_at": qr_code["created_at"],
            "total_amount": qr_code["total_amount"],
            "user_email": users_collection.find_one({"_id": ObjectId(qr_code["user_id"])}).get("email")
        })
    return qr_list