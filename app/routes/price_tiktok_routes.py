from fastapi import HTTPException, APIRouter
from pydantic import BaseModel

from app.config.database import pricing_tiktok_collection

pricing_tiktok_router = APIRouter()

class PriceUpdate(BaseModel):
    new_price: int

# GET endpoint to retrieve the current price
@pricing_tiktok_router.get("/", response_description = "Current price per TikTok ID")
async def get_price():
    """Retrieve the current price per TikTok ID."""
    current_price = pricing_tiktok_collection.find_one()
    return {"price_tiktok_id": current_price.get("pricing_tiktok")}

# PUT endpoint to update the price
@pricing_tiktok_router.put("/", response_description="Update price per TikTok ID")
async def update_price(price_update: PriceUpdate):
    """Update the price per TikTok ID."""
    if price_update.new_price < 0:
        raise HTTPException(status_code=400, detail="Giá phải là số dương.")

    pricing_tiktok_collection.update_one({}, {"$set": {"pricing_tiktok": price_update.new_price}})
    return {"message": "Cập nhật giá thành công", "pricing_tiktok": price_update.new_price}
