from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, status
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import asyncio
from app.config.database import global_customers_collection, local_customers_collection
from app.middlewares.auth_middleware import auth_middleware
from TikTokLive.client.web.web_settings import WebDefaults
import os

EULER_API_KEY_1 = os.getenv("EULER_API_KEY_1")
WebDefaults.tiktok_sign_api_key = EULER_API_KEY_1

ws_router = APIRouter()

# # WebSocket handler
# async def handle_tiktok_live(websocket: WebSocket, tiktok_id: str):
#     client = TikTokLiveClient(tiktok_id)
#
#     @client.on(CommentEvent)
#     async def on_comment(event: CommentEvent):
#         comment = {
#             "room_id": str(event.common.room_id),
#             "msg_id": str(event.common.msg_id),
#             "from_live_of_tiktok_id": tiktok_id,
#             "customer_user_id": str(event.user.id),
#             "customer_tiktok_id": event.user.unique_id,
#             "customer_name": event.user.nickname,
#             "comment": event.comment,
#             "profile_picture_url": event.user.avatar_thumb.url_list[0],
#             "created_at": datetime.fromtimestamp(int(event.common.create_time / 1000)).isoformat()
#         }
#         try:
#             await websocket.send_json(comment)
#         except:
#             pass
#
#     # Start the TikTokLive client
#     asyncio.create_task(client.start())
#     try:
#         while True:
#             await asyncio.sleep(1)  # Keep WebSocket connection alive
#     except WebSocketDisconnect:
#         print(f"WebSocket disconnected for username: {tiktok_id}")
#     finally:
#         # Ensure the client is stopped
#         await client.disconnect(close_client = True)
#         await asyncio.sleep(0.1)

# WebSocket handler for multiple TikTok IDs
async def handle_tiktok_live(websocket: WebSocket, tiktok_ids: list[str], user_id: str):
    clients = []

    print(f"User ID {user_id} connecting ws: {tiktok_ids}")

    for tiktok_id in tiktok_ids:
        client = TikTokLiveClient(tiktok_id)

        # Use a closure to capture the current tiktok_id
        def make_on_comment_handler(current_tiktok_id):
            async def on_comment(event: CommentEvent):
                customer_user_id = str(event.user.id)
                global_customer = global_customers_collection.find_one({"customer_user_id": customer_user_id})
                local_customer = local_customers_collection.find_one({"customer_user_id": customer_user_id, "from_live_of_tiktok_id": current_tiktok_id, "user_id": user_id })
                comment = {
                    "room_id": str(event.common.room_id),
                    "msg_id": str(event.common.msg_id),
                    "from_live_of_tiktok_id": current_tiktok_id,  # Use the captured tiktok_id
                    "customer_user_id": customer_user_id,
                    "customer_tiktok_id": event.user.unique_id,
                    "customer_name": event.user.nickname,
                    "comment": event.comment,
                    "profile_picture_url": event.user.avatar_thumb.url_list[0],
                    "created_at": datetime.fromtimestamp(int(event.common.create_time / 1000)).isoformat(),
                    "has_global_phone": bool(global_customer and global_customer.get("phone") and len(global_customer["phone"]) > 0),
                    "has_local_phone": bool(
                        local_customer and local_customer.get("phone") and len(local_customer["phone"]) > 0
                        ),
                }
                try:
                    await websocket.send_json(comment)
                except:
                    pass

            return on_comment

        # Bind the tiktok_id to the event handler
        client.on(CommentEvent)(make_on_comment_handler(tiktok_id))

        # Start the TikTokLive client
        asyncio.create_task(client.start())
        clients.append(client)

    try:
        while True:
            await asyncio.sleep(1)  # Keep WebSocket connection alive
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for usernames: {tiktok_ids}")
    finally:
        # Ensure all clients are stopped
        for client in clients:
            await client.disconnect(close_client=True)
        await asyncio.sleep(0.1)

# WebSocket endpoint
@ws_router.websocket("/{usernames}")
async def websocket_endpoint(websocket: WebSocket, usernames: str, token: str):
    await websocket.accept()
    try:
        user = await auth_middleware(token)
        if not user:
            await websocket.close(code = status.WS_1008_POLICY_VIOLATION)  # Close with error code
            return
        tiktok_ids = usernames.split(",")
        await handle_tiktok_live(websocket, tiktok_ids, str(user.get('_id')))
    except WebSocketDisconnect:
        print("WebSocket disconnected")