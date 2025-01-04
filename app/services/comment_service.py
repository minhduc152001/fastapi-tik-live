from pymongo.errors import DuplicateKeyError

from app.config.database import comments_collection
from app.models.comment_model import Comment, CommentResponse


async def create_comment_service(comment: Comment) -> CommentResponse:
    try:
        comment_dict = comment.model_dump()
        new_comment = comments_collection.insert_one(comment_dict)
        comment_id = str(new_comment.inserted_id)
        comment_dict["id"] = comment_id
        return CommentResponse(**comment_dict)
    except DuplicateKeyError:
        existing_comment = comments_collection.find_one({
            "msg_id": comment.msg_id,
            "user_id": comment.user_id,
        })
        if existing_comment:
            existing_comment["id"] = str(existing_comment["_id"])
            return CommentResponse(**existing_comment)