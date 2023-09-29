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
    attachments: list[AttachmentModelBody]
    # teacher_id: str


class PostCourseAnnouncementResponseModel(BaseModel):
    announcement_id: str


class TeacherModelBody(BaseModel):
    teacher_id: str
    teacher_name: str
class GetCourseAnnouncementResponseModel(BaseModel):
    announcement_id: str
    teacher: str # TODO: change to TeacherModelBody
    name: str
    last_edit: int
    text: str
    attachments: list[AttachmentModelBody]
