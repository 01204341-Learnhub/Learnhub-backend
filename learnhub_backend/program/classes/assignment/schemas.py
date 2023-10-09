from typing import Optional, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from bson import ObjectId


# ASSIGNMENTS
class AttachmentPatchModelBody(BaseModel):
    op: str  # add | delete
    src: str


class PatchAssignmentRequestModel(BaseModel):
    name: str | None = None
    group_name: str | None = None
    due_time: int | None = None
    status: str | None = None
    text: str | None = None
    max_score: int | None = None
    attachments: list[AttachmentPatchModelBody] | None = None
