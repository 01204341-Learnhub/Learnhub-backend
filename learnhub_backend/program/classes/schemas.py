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
    description: str
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
    open_time: int
    class_ended_date: int


class PostClassResponseModel(BaseModel):
    class_id: str


class PatchClassObjectiveModelBody(BaseModel):
    op: str  # add | delete | edit | swap
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
    open_time: int | None = None
    registration_ended_date: int | None = None
    class_ended_date: int | None = None


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
