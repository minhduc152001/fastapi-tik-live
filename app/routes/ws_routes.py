from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent
import asyncio

ws_router = APIRouter()

# Dictionary to manage TikTokLive clients per username
clients = {}


@ws_router.websocket("/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    try:
        if username not in clients:
            # Start TikTokLive client for the username
            client = TikTokLiveClient(username)

            @client.on(CommentEvent)
            async def on_comment(event: CommentEvent):
                comment = {
                    "room_id": str(event.common.room_id),
                    "msg_id": str(event.common.msg_id),
                    "from_live_of_tiktok_id": event.at_user.unique_id,
                    "customer_user_id": str(event.user.id),
                    "customer_tiktok_id": event.user.unique_id,
                    "customer_name": event.user.nickname,
                    "comment": event.comment,
                    "profile_picture_url": event.user.avatar_thumb.url_list[0],
                    "created_at": datetime.fromtimestamp(int(event.common.create_time / 1000)).isoformat()
                }
                # Send comments to the WebSocket
                try:
                    await websocket.send_json(comment)
                except WebSocketDisconnect:
                    print(f"WebSocket disconnected for username: {username}")

            # Save the client
            clients[username] = client
            # Run the TikTokLive client asynchronously
            asyncio.create_task(client.start())

        # Keep the WebSocket connection alive
        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for username: {username}")
        # Cleanup when WebSocket disconnects
        if username in clients:
            client = clients[username]
            client.stop()
            del clients[username]