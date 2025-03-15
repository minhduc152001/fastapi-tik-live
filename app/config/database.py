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
local_customers_collection = database["local-customers"]
global_customers_collection = database["global-customers"]
order_collection = database["orders"]
banks_collection = database["banks"]
qr_collection = database["qr"]
sms_collection = database["sms"]
balance_movements_collection = database["balance-movements"]
invoices_collection = database["invoices"]
prices_collection = database["prices"]
pricing_tiktok_collection = database["pricing-tiktok"]

# Set unique
rooms_collection.create_index([("room_str_id", 1), ("user_id", 1)], unique=True)
comments_collection.create_index([("msg_id", 1), ("room_id", 1)], unique=True)
order_collection.create_index([("msg_id", 1)], unique=True)
local_customers_collection.create_index([("customer_user_id", 1), ("from_live_of_tiktok_id", 1)], unique=True)
global_customers_collection.create_index([("customer_user_id", 1)], unique=True)
qr_collection.create_index([("payment_description", 1)], unique=True)
sms_collection.create_index([("msg", 1)], unique=True)
invoices_collection.create_index([("invoice_id", 1)], unique=True)