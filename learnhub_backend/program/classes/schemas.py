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
    description: str
    status: str
    tags: list[TagModelBody]
    registration_ended_date: int
    open_date: int
    class_ended_date: int
    price: float


class ListClassesResponseModel(BaseModel):
    classes: list[ListClassesModelBody]


class GetClassResponseModel(BaseModel):
    class_id: str
    name: str
    class_pic: HttpUrl
    teacher: TeacherModelBody
    description: str
    tags: list[TagModelBody]
    status: str
    schedules: list[ScheduleModelBody]
    registration_ended_date: int  # datetime
    open_date: int  # datetime
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


class PostClassRequestModel(BaseModel):
    name: str
    class_pic: HttpUrl
    teacher_id: str
    max_student: int
    price: float
    description: str
    class_objective: list[str]
    class_requirement: str
    difficulty_level: str
    tag_ids: list[str]  # listOf[tag_id]
    schedules: list[ScheduleModelBody]
    registration_ended_date: int
    open_date: int
    class_ended_date: int


class PostClassResponseModel(BaseModel):
    class_id: str


class PatchClassObjectiveModelBody(BaseModel):
    op: str  # add | remove
    value: str


class PatchTagModelBody(BaseModel):
    op: str  # add | remove
    tag_id: str  # tag_id


class PatchClassScheduleModelBody(BaseModel):
    op: str
    start: int
    end: int


class PatchClassRequestModel(BaseModel):
    name: str | None = None
    class_pic: HttpUrl | None = None
    max_student: int | None = None
    price: float | None = None
    description: str | None = None
    class_objective: list[PatchClassObjectiveModelBody] | None = None
    class_requirement: str | None = None
    difficulty_level: str | None = None
    tag: PatchTagModelBody | None = None
    schedules: PatchClassScheduleModelBody | None = None
    open_date: int | None = None
    registration_ended_date: int | None = None
    class_ended_date: int | None = None


# THREADS
class ListThreadModelBody(BaseModel):
    thread_id: str
    name: str
    teacher: TeacherModelBody
    last_edit: int


class ListThreadResponseModel(BaseModel):
    threads: list[ListThreadModelBody]


class PostThreadAttachmentModelBody(BaseModel):
    # attachment_type: str
    src: str


class PostThreadRequestModel(BaseModel):
    name: str
    text: str
    attachments: list[PostThreadAttachmentModelBody]


class PostThreadResponseModel(BaseModel):
    thread_id: str


class AttachmentModelBody(BaseModel):
    attachment_type: str
    src: str


class GetThreadResponseModel(BaseModel):
    name: str
    teacher: TeacherModelBody
    last_edit: int
    text: str
    attachments: list[AttachmentModelBody]


class PatchThreadAttachmentModelBody(BaseModel):
    op: str # add | remove
    src: str


class PatchThreadRequestModel(BaseModel):
    name: str | None = None
    text: str | None = None
    attachments: list[PatchThreadAttachmentModelBody] | None = None
