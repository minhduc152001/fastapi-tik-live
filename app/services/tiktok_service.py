from datetime import datetime

from TikTokLive import TikTokLiveClient
from fastapi import HTTPException
from TikTokLive.events import ConnectEvent, CommentEvent, LiveEndEvent, DisconnectEvent

from app.models.comment_model import Comment
from app.models.customer_model import Customer
from app.models.live_model import LiveConnectResponse
from app.services.comment_service import create_comment_service
from app.services.customer_service import create_customer_service
from app.services.room_service import create_room_service, check_room_online, update_room_service
from app.models.room_model import Room, RoomUpdateRequest


class LiveTikTokHandler:
    def __init__(self):
        self.room_db_id: str = ""

async def connect_live_service(tiktok_id: str, user_id: str):
    # Check if current ID is online to raise an error
    another_room_live = await check_room_online(tiktok_id, user_id)
    if another_room_live:
        raise HTTPException(status_code=400, detail = "You just have turn this room online!")

    client: TikTokLiveClient = TikTokLiveClient(unique_id=f"@{tiktok_id}")

    live_handler = LiveTikTokHandler()

    try:
        is_live = await client.is_live()

        if not is_live:
            raise HTTPException(status_code=400, detail="Live stream is currently offline")

        print(f"{tiktok_id} is live!")
        await client.start(fetch_room_info=True)

        @client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            title = ""
            nickname = ""
            room_info = client.room_info
            if room_info is not None:
                title = room_info.get("title")
                nickname = room_info.get("owner").get("nickname")

            # Create room is_live: True
            created_at = datetime.now()
            new_room = await create_room_service(
                Room(room_str_id = str(event.room_id), is_live = True, title = title, nickname = nickname,
                     user_id = user_id, tiktok_id = tiktok_id, created_at = created_at, updated_at = created_at
                     )
                )
            live_handler.room_db_id = new_room.id

        @client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            try:
                commented_at = datetime.fromtimestamp(int(event.common.create_time / 1000))
                # Create customer
                customer = await create_customer_service(Customer(
                    user_id = user_id,
                    tiktok_id = tiktok_id,
                    tiktok_user_id = str(event.user.unique_id),
                    display_name = event.user.nickname,
                    profile_picture_url = event.user.avatar_thumb.url_list[0],
                    created_at = commented_at,
                ))

                # Create comment
                room_id = live_handler.room_db_id
                comment = await create_comment_service(Comment(
                    room_id = room_id,
                    user_id = user_id,
                    msg_id = str(event.common.msg_id),
                    customer_id = customer.id,
                    customer_name = customer.display_name,
                    comment = event.comment,
                    created_at = commented_at
                ))
            except e:
                raise HTTPException(status_code=500, detail = f"{e}")

        @client.on(LiveEndEvent)
        async def on_live_end(_: DisconnectEvent):
            room_id = live_handler.room_db_id
            # Update ended_at: now(), is_live: False of room in DB
            now = datetime.now()
            await update_room_service(room_id, {
                "is_live": False,
                "ended_at": now,
                "updated_at": now,
            })
            # await client.disconnect() # No need, it includes the livestream ending when ending
            print(f"Live of {tiktok_id} ended!")

        message = "Successfully connected to the live stream"
        return LiveConnectResponse(is_live = is_live, message = message)

    except Exception as e:
        print(f"Error connecting to live: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")
