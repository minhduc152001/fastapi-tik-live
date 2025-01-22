from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import asyncio

ws_router = APIRouter()

# WebSocket handler
async def handle_tiktok_live(websocket: WebSocket, tiktok_id: str):
    client = TikTokLiveClient(tiktok_id)

    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        comment = {
            "room_id": str(event.common.room_id),
            "msg_id": str(event.common.msg_id),
            "from_live_of_tiktok_id": tiktok_id,
            "customer_user_id": str(event.user.id),
            "customer_tiktok_id": event.user.unique_id,
            "customer_name": event.user.nickname,
            "comment": event.comment,
            "profile_picture_url": event.user.avatar_thumb.url_list[0],
            "created_at": datetime.fromtimestamp(int(event.common.create_time / 1000)).isoformat()
        }
        try:
            await websocket.send_json(comment)
        except:
            pass

    # Start the TikTokLive client
    asyncio.create_task(client.start())
    try:
        while True:
            await asyncio.sleep(1)  # Keep WebSocket connection alive
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for username: {tiktok_id}")
    finally:
        # Ensure the client is stopped
        await client.disconnect(close_client = True)
        await asyncio.sleep(0.1)

# WebSocket endpoint
@ws_router.websocket("/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    await handle_tiktok_live(websocket, username)
