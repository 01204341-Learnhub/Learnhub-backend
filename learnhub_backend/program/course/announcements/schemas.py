from datetime import datetime
from typing import Any
from pydantic import BaseModel, HttpUrl

class ListCourseAnnouncementsModelBody(BaseModel):
    announcement_id: str
    last_edit: int
    name: str

class ListCourseAnnouncementsResponseModel(BaseModel):
    annoucements: list[ListCourseAnnouncementsModelBody]

class AttachmentModelBody(BaseModel):
    attachment_type: str
    src: HttpUrl
class PostCourseAnnouncementRequestModel(BaseModel):
    name: str
    text: str
    attachments: list[Any]
    #teacher_id: str
