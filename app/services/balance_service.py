from typing import List
import pymongo
from app.config.database import balance_movements_collection


async def list_balances_service():
    balances = balance_movements_collection.find().sort("_id", pymongo.ASCENDING)
    balance_list: List[dict] = []
    for balance in balances:
        balance_list.append({
            "id": str(balance['_id']),
            "account_number": balance['account_number'],
            "amount": balance['amount'],
            "transaction_time": balance['transaction_time'],
            "current_balance": balance['current_balance'],
            "payment_description": balance['payment_description'],
        }
        )
    return balance_list