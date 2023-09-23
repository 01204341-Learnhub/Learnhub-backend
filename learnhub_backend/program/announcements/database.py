from datetime import datetime
from bson.objectid import ObjectId

from learnhub_backend.program.announcements.schemas import PostCourseAnnouncementRequestModel
from ..database import db_client


def list_course_announcement( course_id: str, skip: int = 0, limit: int = 100):
    q = {"course_id": ObjectId(course_id)}
    
    annoucements_cursor = db_client.annoucement_coll.find(q, skip=skip, limit=limit)
    annoucements = []
    for annoucement in annoucements_cursor:
        annoucement["announcement_id"] = str(annoucement["_id"])
        annoucement["course_id"] = str(annoucement["course_id"])
        annoucement["teacher_id"] = str(annoucement["teacher_id"])
        del annoucement["_id"]
        annoucements.append(annoucement)
    return annoucements

def create_course_announcement(course_id: str, announcement_body: PostCourseAnnouncementRequestModel):
    announcement_body_to_inserted = announcement_body.model_dump()
    announcement_body_to_inserted["course_id"] = ObjectId(course_id)
    announcement_body_to_inserted["last_edit"] = datetime.now()
    response = db_client.annoucement_coll.insert_one(announcement_body_to_inserted)
    created_id = response.inserted_id
    return str(created_id)
