from pydantic import BaseModel, HttpUrl


# STUDENT
class StudentModelBody(BaseModel):
    student_id: str
    student_name: str
    profile_pic: str | None = None


# ATTACHMENT
class AttachmentModelBody(BaseModel):
    attachment_type: str
    src: str


class AttachmentPatchModelBody(BaseModel):
    op: str  # add | remove
    attachment_type: str
    src: str


# ASSIGNMENTS
class SubmissionCountModelBody(BaseModel):
    submit_count: int
    unsubmit_count: int


class ListClassAssignmentsModelBody(BaseModel):
    assignment_id: str
    name: str
    group_name: str
    last_edit: int
    due_date: int
    status: str
    max_score: float
    submission_count: SubmissionCountModelBody
    text: str


class ListClassAssignmentsResponseModel(BaseModel):
    assignments: list[ListClassAssignmentsModelBody]


class GetClassAssignmentResponseModel(BaseModel):
    name: str
    group_name: str
    last_edit: int
    due_date: int
    status: str
    max_score: float
    text: str
    attachments: list[AttachmentModelBody]


class PostClassAssignmentRequestModel(BaseModel):
    name: str
    group_name: str
    due_date: int
    text: str
    max_score: float
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


# SUBMISSION
class ListAssignmentSubmissionModelBody(BaseModel):
    status: str  # check | uncheck | unsubmit
    score: float
    submission_date: int
    student: StudentModelBody


class ListAssignmentSubmissionResponseModel(BaseModel):
    submissions: list[ListAssignmentSubmissionModelBody]


class GetAssignmentSubmissionResponseModel(BaseModel):
    status: str  # check | uncheck | unsubmit
    score: float
    submission_date: int
    student: StudentModelBody
    attachments: list[AttachmentModelBody]


class PatchAssignmentSubmissionScoreRequestModel(BaseModel):
    score: float  # max 100


class PutAssignmentSubmitRequestModel(BaseModel):
    attachments: list[AttachmentModelBody]


class PutAssignmentSubmitResponseModel(BaseModel):
    student_id: str
