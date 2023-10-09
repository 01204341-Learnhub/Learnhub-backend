from datetime import datetime
from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import UpdateResult

from ....dependencies import GenericOKResponse

from .schemas import (
    ListClassAssignmentsModelBody,
    ListClassAssignmentsResponseModel,
    PatchAssignmentRequestModel,
)

from .database import (
    query_assignments_by_class_id,
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


def patch_assignment_request(
    class_id: str, assignment_id: str, patch_body: PatchAssignmentRequestModel
):
    response = edit_assignment(
        class_id=class_id, assignment_id=assignment_id, patch_body_=patch_body
    )
    return GenericOKResponse
