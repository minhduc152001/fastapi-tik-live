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
        raise HTTPException(400, "Thiếu mã ngân hàng (VCB, ACB...)")
    details_dict["user_id"] = user_id
    details_dict["payment_description"] = None
    details_dict["created_at"] = datetime.now()
    details_dict["total_amount"] = details.total_month_cost + details.total_tiktok_ids * PRICE_PER_TIKTOK_ID
    new_qr_id = qr_collection.insert_one(details_dict).inserted_id
    payment_description = f"HoaDon{new_qr_id}"
    qr = qr_collection.find_one_and_update({"_id": ObjectId(new_qr_id)}, {"$set": {"payment_description": payment_description}})
    return {
        "bank_name": qr.get("bank_name"),
        "account_number": qr.get("account_number"),
        "bank_code": qr.get("bank_code"),
        "total_amount": qr.get("total_amount"),
        "payment_description": payment_description,
        "url": f"https://qr.sepay.vn/img?acc={qr.get("account_number")}&bank={qr.get("bank_code")}&amount={qr.get("total_amount")}&des={payment_description}"
    }


async def list_qr_codes_service():
    qr_codes = qr_collection.find().to_list(length = None)
    user_ids = [ObjectId(qr["user_id"]) for qr in qr_codes]
    users = {str(user["_id"]): user.get("email") for user in
            users_collection.find({"_id": {"$in": user_ids}}).to_list(length = None)}
    return [
        {
            "id": str(qr["_id"]),
            "user_email": users.get(qr["user_id"]),
            **{k: qr[k] for k in ["bank_code", "account_number", "total_month_cost", "total_months",
                                  "total_tiktok_ids", "bank_name", "payment_description", "created_at", "total_amount"]}
        }
        for qr in qr_codes
    ]
