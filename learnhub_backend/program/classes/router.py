from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ...dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    list_classes_response,
    get_class_response,
    patch_assignment_request,
    patch_class_request,
    post_class_request,
    list_threads_response,
    post_thread_request,
    get_thread_response,
)

from .schemas import (
    ListClassesResponseModel,
    GetClassResponseModel,
    PatchAssignmentRequestModel,
    PatchClassRequestModel,
    PostClassRequestModel,
    PostClassResponseModel,
    ListThreadResponseModel,
    PostThreadRequestModel,
    PostThreadResponseModel,
    GetThreadResponseModel,
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


# CLASSES
@router.get(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListClassesResponseModel,
)
def list_classes(common_paginations: common_page_params):
    response_body = list_classes_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


@router.post(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostClassResponseModel,
)
def post_class(requestBody: PostClassRequestModel):
    response_body = post_class_request(requestBody)
    return response_body


@router.get(
    "/{class_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetClassResponseModel,
)
def get_class(class_id: str):
    response_body = get_class_response(class_id=class_id)
    return response_body


@router.patch(
    "/{class_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def patch_class(class_id: str, request_body: PatchClassRequestModel):
    response_body = patch_class_request(class_id, request_body)
    return response_body


# THREADS
@router.get(
    "/{class_id}/threads",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListThreadResponseModel,
)
def list_threads(class_id: str, common_paginations: common_page_params):
    response_body = list_threads_response(
        class_id=class_id,
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


@router.post(
    "/{class_id}/threads",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostThreadResponseModel,
)
def post_thread(class_id: str, thread_body: PostThreadRequestModel):
    response_body = post_thread_request(class_id=class_id, thread_body=thread_body)
    return response_body


@router.get(
    "/{class_id}/threads/{thread_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetThreadResponseModel,
)
def get_thread(class_id: str, thread_id: str):
    response_body = get_thread_response(class_id=class_id, thread_id=thread_id)
    return response_body


# ASSIGNMENTS
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
