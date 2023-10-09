from typing import Optional, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from bson import ObjectId


# ATTACHMENT
class AttachmentModelBody(BaseModel):
    attachment_type: str
    src: str


class AttachmentPatchModelBody(BaseModel):
    op: str  # add | remove
    attachment_type: str
    src: str


# ASSIGNMENTS
class ListClassAssignmentsModelBody(BaseModel):
    assignment_id: str
    name: str
    group_name: str
    last_edit: int
    due_date: int
    status: str
    text: str


class ListClassAssignmentsResponseModel(BaseModel):
    assignments: list[ListClassAssignmentsModelBody]


class GetClassAssignmentResponseModel(BaseModel):
    name: str
    group_name: str
    last_edit: int
    due_date: int
    status: str
    text: str
    attachments: list[AttachmentModelBody]


class PostClassAssignmentRequestModel(BaseModel):
    name: str
    group_name: str
    due_date: int
    text: str
    attachments: list[AttachmentModelBody]


class PostClassAssignmentResponseModel(BaseModel):
    assignment_id: str


class PatchAssignmentRequestModel(BaseModel):
    name: str | None = None
    due_date: int | None = None
    status: str | None = None  # open | closed
    group_name: str | None = None
    text: str | None = None
    attachments: list[AttachmentPatchModelBody] | None = None
