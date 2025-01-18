from typing import List

from bson import ObjectId

from app.config.database import prices_collection
from app.models.price_model import PriceRequest


async def list_prices_service():
    prices = prices_collection.find()
    list_prices: List[dict] = []
    for price in prices:
        list_prices.append({
            'id': str(price['_id']),
            'amount_per_month': price['amount_per_month'],
            'total_tiktok_ids': price['total_tiktok_ids'],
            'total_months': price['total_months'],
        })
    return list_prices

async def create_price_service(data: PriceRequest):
    data_dict = data.model_dump()
    new_price_id = prices_collection.insert_one(data_dict).inserted_id
    return {
        'id': str(new_price_id),
        'amount_per_month': data.amount_per_month,
        'total_tiktok_ids': data.total_tiktok_ids,
        'total_months': data.total_months,
    }

async def update_price_service(price_id: str, data: PriceRequest):
    data_dict = data.model_dump()
    prices_collection.update_one({"_id": ObjectId(price_id)}, {"$set": data_dict})
    return {
        'id': str(price_id),
        'amount_per_month': data.amount_per_month,
        'total_tiktok_ids': data.total_tiktok_ids,
        'total_months': data.total_months,
    }

async def delete_price_service(price_id: str):
    prices_collection.delete_one({"_id": ObjectId(price_id)})