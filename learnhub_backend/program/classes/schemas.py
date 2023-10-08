from typing import Optional, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from bson import ObjectId


# CLASSES
class TeacherModelBody(BaseModel):
    teacher_id: str
    teacher_name: str
    profile_pic: HttpUrl


class TagModelBody(BaseModel):
    tag_id: str
    tag_name: str


class ScheduleModelBody(BaseModel):
    start: int
    end: int


class ListClassesModelBody(BaseModel):
    class_id: str
    name: str
    class_pic: HttpUrl
    teacher: TeacherModelBody
    status: str
    tags: list[TagModelBody]
    registration_ended_date: int
    open_time: int
    class_ended_date: int
    price: float


class ListClassesResponseModel(BaseModel):
    classes: list[ListClassesModelBody]


class GetClassResponseModel(BaseModel):
    class_id: str
    name: str
    class_pic: HttpUrl
    teacher: TeacherModelBody
    tags: list[TagModelBody]
    status: str
    schedules: list[ScheduleModelBody]
    registration_ended_date: int  # datetime
    open_time: int  # datetime
    class_ended_date: int  # datetime
    price: float
    class_objective: list[str]
    class_requirement: str
    difficulty_level: str
    chapter_count: int
    meeting_count: int
    student_count: int
    max_student: int
    assignment_count: int


# ASSIGNMENTS


class AttachmentPatchModelBody(BaseModel):
    op: str  # add | delete | edit
    old_src: str | None = None
    new_src: str | None = None


class PatchAssignmentRequestModel(BaseModel):
    name: str | None = None
    due_date: int | None = None
    status: str | None = None
    text: str | None = None
    attachments: list[AttachmentPatchModelBody] | None = None
