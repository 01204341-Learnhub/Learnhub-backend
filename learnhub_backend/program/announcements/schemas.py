from datetime import datetime
from typing import Any
from pydantic import BaseModel

class ListCourseAnnouncementsModelBody(BaseModel):
    announcement_id: str
    course_id: str
    last_edit: datetime
    name: str
    teacher_id: str
    text: str
    attachments: list[Any]

class ListCourseAnnouncementsResponseModel(BaseModel):
    annoucements: list[ListCourseAnnouncementsModelBody]

class PostCourseAnnouncementRequestModel(BaseModel):
    name: str
    text: str
    attachments: list[Any]
    teacher_id: str
