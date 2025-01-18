from typing import List

from app.config.database import sms_collection


async def get_all_sms_service():
    list_sms = sms_collection.find()
    sms_list_tmp: List[dict] = []
    for sms in list_sms:
        sms_list_tmp.append({
            "id": str(sms['_id']),
            "sender": sms['sender'],
            "msg": sms['msg'],
        })
    return sms_list_tmp