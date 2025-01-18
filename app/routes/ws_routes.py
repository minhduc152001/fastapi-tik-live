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
                # Send comments to the WebSocket
                try:
                    await websocket.send_text(event.comment)
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