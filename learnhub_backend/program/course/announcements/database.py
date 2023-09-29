from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo.results import InsertOneResult

from .schemas import PostCourseAnnouncementRequestModel
from learnhub_backend.database import db_client
from learnhub_backend.dependencies import (
    Exception,
)


def list_course_announcement(course_id: str, skip: int = 0, limit: int = 100):
    try:
        q = {"course_id": ObjectId(course_id)}

        announcements_cursor = db_client.annoucement_coll.find(
            q, skip=skip, limit=limit
        )
        announcements = []
        for announcement in announcements_cursor:
            announcement["announcement_id"] = str(announcement["_id"])
            announcement["last_edit"] = int(datetime.timestamp(announcement["last_edit"]))
            announcements.append(announcement)
    except InvalidId:
        raise Exception.bad_request
    return announcements


def create_course_announcement(
    course_id: str, announcement_body: PostCourseAnnouncementRequestModel
) -> str:
    announcement_body_to_inserted = announcement_body.model_dump()
    announcement_body_to_inserted["course_id"] = ObjectId(course_id)
    announcement_body_to_inserted["last_edit"] = datetime.now(tz=timezone(timedelta(hours=7))) # bangkok time
    for i in range(len(announcement_body_to_inserted["attachments"])):
        announcement_body_to_inserted["attachments"][i]["src"] = str(announcement_body_to_inserted["attachments"][i]["src"])
    response = db_client.annoucement_coll.insert_one(announcement_body_to_inserted)
    created_id = response.inserted_id
    return str(created_id)
