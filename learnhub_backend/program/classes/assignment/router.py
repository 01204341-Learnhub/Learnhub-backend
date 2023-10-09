from fastapi import APIRouter, Depends
from typing import Annotated, Union

from ....dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .schemas import (
    GetAssignmentSubmissionResponseModel,
    GetClassAssignmentResponseModel,
    ListAssignmentSubmissionResponseModel,
    ListClassAssignmentsResponseModel,
    PatchAssignmentRequestModel,
    PostClassAssignmentRequestModel,
    PostClassAssignmentResponseModel,
    PutAssignmentSubmitRequestModel,
    PutAssignmentSubmitResponseModel,
)

from .services import (
    get_assignment_response,
    get_assignment_submission_response,
    list_assignment_response,
    list_assignment_submissions_response,
    patch_assignment_request,
    patch_assignment_unsubmit_request,
    post_assignment_request,
    put_assignment_submit_request,
)

router = APIRouter(
    prefix="/programs/classes",
    tags=["classes"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


# ASSIGNMENTS
@router.get(
    "/{class_id}/assignments",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListClassAssignmentsResponseModel,
)
def list_assignment(class_id: str):
    response_body = list_assignment_response(class_id)
    return response_body


@router.post(
    "/{class_id}/assignments",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostClassAssignmentResponseModel,
)
def post_assignment(class_id: str, request_body: PostClassAssignmentRequestModel):
    response_body = post_assignment_request(class_id, request_body)
    return response_body


@router.get(
    "/{class_id}/assignments/{assignment_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetClassAssignmentResponseModel,
)
def get_assignment(class_id: str, assignment_id: str):
    response_body = get_assignment_response(class_id, assignment_id)
    return response_body


@router.patch(
    "/{class_id}/assignments/{assignment_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def patch_assignment(
    class_id: str, assignment_id: str, patch_body: PatchAssignmentRequestModel
):
    response_body = patch_assignment_request(
        class_id=class_id, assignment_id=assignment_id, patch_body=patch_body
    )
    return response_body


# TODO: Delete assignment


# SUBMISSION
@router.get(
    "/{class_id}/assignments/{assignment_id}/submissions",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListAssignmentSubmissionResponseModel,
)
def list_assignment_submissions(class_id: str, assignment_id: str):
    response_body = list_assignment_submissions_response(class_id, assignment_id)
    return response_body


@router.get(
    "/{class_id}/assignments/{assignment_id}/submissions/{student_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetAssignmentSubmissionResponseModel,
)
def get_assignment_submission(class_id: str, assignment_id: str, student_id: str):
    response_body = get_assignment_submission_response(
        class_id, assignment_id, student_id
    )
    return response_body


@router.put(
    "/{class_id}/assignments/{assignment_id}/submissions/{student_id}/submit",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PutAssignmentSubmitResponseModel,
)
def put_assignment_submit(
    class_id: str,
    assignment_id: str,
    student_id: str,
    request_body: PutAssignmentSubmitRequestModel,
):
    response_body = put_assignment_submit_request(
        class_id, assignment_id, student_id, request_body
    )
    return response_body


@router.patch(
    "/{class_id}/assignments/{assignment_id}/submissions/{student_id}/unsubmit",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def patch_assignment_unsubmit(class_id: str, assignment_id: str, student_id: str):
    response_body = patch_assignment_unsubmit_request(
        class_id, assignment_id, student_id
    )
    return response_body
