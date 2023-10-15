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


# REPLIES
class UserReplyModelBody(BaseModel):
    user_id: str
    user_type: str
    name: str
    profile_pic: HttpUrl


class ReplyModelBody(BaseModel):
    user: UserReplyModelBody
    reply_date: int
    text: str


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
    replies: list[ReplyModelBody]


class PostAssignmentReplyRequestModel(BaseModel):
    user_id: str
    user_type: str
    text: str


class PostAssignmentReplyResponseModel(BaseModel):
    assignment_reply_id: str


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
    replies: list[ReplyModelBody]


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
