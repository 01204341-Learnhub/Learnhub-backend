from datetime import datetime, timezone, timedelta
from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import UpdateResult

from ....dependencies import GenericOKResponse, Exception, CheckHttpFileType

from .schemas import (
    AttachmentModelBody,
    GetClassAssignmentResponseModel,
    ListClassAssignmentsModelBody,
    ListClassAssignmentsResponseModel,
    PatchAssignmentRequestModel,
    PostClassAssignmentRequestModel,
    PostClassAssignmentResponseModel,
)

from .database import (
    create_assignment,
    query_assignments_by_class_id,
    query_single_assignment,
    edit_assignment,
)


# ASSIGNMENTS
def list_assignment_response(class_id: str) -> ListClassAssignmentsResponseModel:
    assignments_cur = query_assignments_by_class_id(class_id)
    assignments = []

    for assg_ in assignments_cur:
        assignments.append(
            ListClassAssignmentsModelBody(
                assignment_id=str(assg_["_id"]),
                name=assg_["name"],
                group_name=assg_["group_name"],
                last_edit=int(datetime.timestamp(assg_["last_edit"])),
                due_date=int(datetime.timestamp(assg_["due_date"])),
                status=assg_["status"],
                text=assg_["text"],
            )
        )
    return ListClassAssignmentsResponseModel(assignments=assignments)


def get_assignment_response(
    class_id: str, assignment_id: str
) -> GetClassAssignmentResponseModel:
    assignment = query_single_assignment(class_id, assignment_id)
    if assignment == None:
        raise Exception.not_found
    ta = TypeAdapter(list[AttachmentModelBody])
    response_body = GetClassAssignmentResponseModel(
        name=assignment["name"],
        group_name=assignment["group_name"],
        last_edit=int(datetime.timestamp(assignment["last_edit"])),
        due_date=int(datetime.timestamp(assignment["due_date"])),
        status=assignment["status"],
        text=assignment["text"],
        attachments=ta.validate_python(assignment["attachments"]),
    )
    return response_body


def post_assignment_request(
    class_id: str, request: PostClassAssignmentRequestModel
) -> PostClassAssignmentResponseModel:
    inserted_id = create_assignment(class_id, request)
    if request.due_date <= datetime.now(tz=timezone(timedelta(hours=7))).timestamp():
        err = Exception.unprocessable_content
        err.__setattr__("detail", "required due_date to be later that present")
    return PostClassAssignmentResponseModel(assignment_id=inserted_id)


def patch_assignment_request(
    class_id: str, assignment_id: str, patch_body: PatchAssignmentRequestModel
):
    response = edit_assignment(
        class_id=class_id, assignment_id=assignment_id, patch_body_=patch_body
    )
    return GenericOKResponse
