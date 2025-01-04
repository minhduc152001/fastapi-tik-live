from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DATABASE = os.getenv("DATABASE")

client = MongoClient(MONGO_URL)
database = client[DATABASE]
users_collection = database["users"]
rooms_collection = database["rooms"]
comments_collection = database["comments"]
customers_collection = database["customers"]

# Set unique
rooms_collection.create_index([("room_str_id", 1), ("user_id", 1)], unique=True)
comments_collection.create_index([("msg_id", 1), ("user_id", 1)], unique=True)
customers_collection.create_index([("tiktok_user_id", 1)], unique=True)