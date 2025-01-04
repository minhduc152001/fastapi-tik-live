from typing import List

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app.config.database import rooms_collection
from app.models.room_model import Room, RoomResponse, RoomUpdateRequest


async def create_room_service(room: Room) -> RoomResponse:
    try:
        room_dict = room.model_dump()
        new_room = rooms_collection.insert_one(room_dict)
        room_id = str(new_room.inserted_id)
        room_dict["id"] = room_id
        return RoomResponse(**room_dict)
    except DuplicateKeyError:
        existing_room = rooms_collection.find_one({
            "room_str_id": room.room_str_id,
            "user_id": room.user_id,
        })
        if existing_room:
            existing_room["id"] = str(existing_room["_id"])
            return RoomResponse(**existing_room)

async def check_room_online(tiktok_id: str, user_id: str) -> bool:
    room = rooms_collection.find_one({
        "user_id": user_id,
        "tiktok_id": tiktok_id,
        "is_live": True,
    })
    if room:
        return True
    return False

async def update_room_service(room_id: str, update_data: dict) -> RoomResponse:
    rooms_collection.update_one({
        "_id": ObjectId(room_id)
    }, {
        "$set": update_data,
    })
    updated_room = rooms_collection.find_one({"_id": ObjectId(room_id)})
    updated_room["id"] = str(updated_room["_id"])
    return RoomResponse(**updated_room)

async def list_room_service(user_id: str) -> List[RoomResponse]:
    updated_rooms = rooms_collection.find({"user_id": user_id})
    room_list = []
    for room in updated_rooms:
        room["id"] = str(room["_id"])  # Convert ObjectId to string
        room_list.append(RoomResponse(**room))  # Unpack dict to create RoomResponse
    return room_list