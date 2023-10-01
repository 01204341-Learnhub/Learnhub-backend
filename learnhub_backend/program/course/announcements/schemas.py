from datetime import datetime
from typing import Any
from pydantic import BaseModel, HttpUrl


class ListCourseAnnouncementsModelBody(BaseModel):
    announcement_id: str
    last_edit: int
    name: str


class ListCourseAnnouncementsResponseModel(BaseModel):
    annoucements: list[ListCourseAnnouncementsModelBody]


class AttachmentPostModelBody(BaseModel):
    #attachment_type: str
    src: HttpUrl


class PostCourseAnnouncementRequestModel(BaseModel):
    name: str
    text: str
    attachments: list[AttachmentPostModelBody]
    # teacher_id: str


class PostCourseAnnouncementResponseModel(BaseModel):
    announcement_id: str


class TeacherModelBody(BaseModel):
    teacher_id: str
    teacher_name: str
    profile_pic: HttpUrl


class AttachmentModelBody(BaseModel):
    attachment_type: str
    src: HttpUrl


class GetCourseAnnouncementResponseModel(BaseModel):
    announcement_id: str
    teacher: TeacherModelBody
    name: str
    last_edit: int
    text: str
    attachments: list[AttachmentModelBody]


class AttachmentPatchModelBody(BaseModel):
    op: str # add | delete | edit
    old_src: str | None = None
    new_src: str | None = None

class PatchCourseAnnouncementRequestModel(BaseModel):
    name: str | None = None
    text: str | None = None
    attachments: list[AttachmentPatchModelBody] | None = None
