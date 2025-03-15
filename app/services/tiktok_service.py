import asyncio
from datetime import datetime, timedelta

from TikTokLive import TikTokLiveClient
from fastapi import HTTPException
from TikTokLive.events import ConnectEvent, CommentEvent, LiveEndEvent, DisconnectEvent

from app.config.database import rooms_collection, comments_collection
from app.models.comment_model import Comment
from app.models.live_model import LiveConnectResponse
from app.services.comment_service import create_comment_service
from app.services.room_service import create_room_service, check_room_online, update_room_service
from app.models.room_model import Room

from fastapi import BackgroundTasks

async def delete_old_records():
    while True:
        try:
            print("Deleting old records...")

            five_days_ago = datetime.now() - timedelta(days = 5)

            # Delete old records in rooms_collection
            result_rooms = rooms_collection.delete_many({"created_at": {"$lt": five_days_ago}})
            print(f"Deleted {result_rooms.deleted_count} old records from rooms_collection")

            # Delete old records in comments_collection
            result_comments = comments_collection.delete_many({"created_at": {"$lt": five_days_ago}})
            print(f"Deleted {result_comments.deleted_count} old records from comments_collection")

        except Exception as e:
            print(f"Error deleting old records: {str(e)}")
        await asyncio.sleep(432000)

async def start_event_listeners(client: TikTokLiveClient, live_handler: object, user_id: str, tiktok_id: str):
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
            Room(
                room_str_id=str(event.room_id),
                is_live=True,
                title=title,
                nickname=nickname,
                user_id=user_id,
                tiktok_id=tiktok_id,
                created_at=created_at,
                updated_at=created_at,
            )
        )
        live_handler.room_db_id = new_room.id

    @client.on(CommentEvent)
    async def on_comment(event: CommentEvent):
        try:
            commented_at = datetime.fromtimestamp(int(event.common.create_time / 1000))
            # Create comment
            await create_comment_service(
                Comment(
                    room_id=live_handler.room_db_id,
                    user_id=user_id,
                    msg_id=str(event.common.msg_id),
                    from_live_of_tiktok_id=tiktok_id,
                    customer_user_id=str(event.user.id),
                    customer_tiktok_id=event.user.unique_id,
                    customer_name=event.user.nickname,
                    comment=event.comment,
                    profile_picture_url=event.user.avatar_thumb.url_list[0],
                    created_at=commented_at,
                )
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{e}")

    @client.on(LiveEndEvent)
    async def on_live_end(_: DisconnectEvent):
        room_id = live_handler.room_db_id
        # Update ended_at: now(), is_live: False of room in DB
        now = datetime.now()
        await update_room_service(
            room_id,
            {
                "is_live": False,
                "ended_at": now,
                "updated_at": now,
            },
        )
        print(f"Live of {tiktok_id} ended!")
    await client.start(fetch_room_info=True)

async def connect_live_service(tiktok_id: str, user_id: str, background_tasks: BackgroundTasks):
    class LiveTikTokHandler:
        def __init__(self):
            self.room_db_id: str = ""

    # Check if current ID is online to raise an error
    another_room_live = await check_room_online(tiktok_id, user_id)
    if another_room_live:
        raise HTTPException(status_code=400, detail=f"Kênh {tiktok_id} đang có một buổi phát trực tiếp khác!")

    client: TikTokLiveClient = TikTokLiveClient(unique_id=f"@{tiktok_id}")
    # client.web.set_session_id('72972926786302131211741950985674')
    live_handler = LiveTikTokHandler()

    try:
        is_live = await client.is_live()
        if not is_live:
            raise HTTPException(status_code=400, detail=f"Kênh {tiktok_id} đang không phát trực tiếp")

        print(f"{tiktok_id} is live!")

        # Add the event listener task to background tasks
        background_tasks.add_task(start_event_listeners, client, live_handler, user_id, tiktok_id)

        message = "Kết nối thành công tới buổi phát trực tiếp"
        return LiveConnectResponse(is_live=is_live, message=message)

    except Exception as e:
        print(f"Error connecting to live: {e}")
        raise HTTPException(status_code=500, detail=f"{e}")


async def check_live_rooms():
    while True:
        try:
            print(f"Checking live rooms at {datetime.now()}")

            # Get all rooms where is_live is true
            live_rooms = rooms_collection.find({"is_live": True})

            for room in live_rooms:
                room_id = str(room["_id"])
                tiktok_id = room["tiktok_id"]

                # Check for comments in the last 30 minutes
                thirty_minutes_ago = datetime.now() - timedelta(minutes = 30)
                recent_comments = comments_collection.count_documents({
                    "room_id": room_id,
                    "created_at": {"$gte": thirty_minutes_ago}
                }
                )

                if recent_comments == 0:  # No new comments in the last 30 minutes
                    # Check TikTok live status
                    client = TikTokLiveClient(unique_id = f"@{tiktok_id}")
                    is_live = await client.is_live()

                    if not is_live:
                        # Update room status
                        rooms_collection.update_one(
                            {"_id": room["_id"]},
                            {
                                "$set": {
                                    "is_live": False,
                                    "ended_at": datetime.now(),
                                    "updated_at": datetime.now()
                                }
                            }
                        )
                        print(f"Room {room_id} marked as offline")

        except Exception as e:
            print(f"Error in check_live_rooms: {str(e)}")

        # Wait 30 minutes before the next check
        await asyncio.sleep(30 * 60)  # 30 minutes in seconds