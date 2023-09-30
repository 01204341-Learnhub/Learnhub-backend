from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ..dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    get_teacher_response,
    list_teachers_response,
    post_teacher_request,
)

from .schemas import (
    GetTeacherResponseModel,
    ListTeachersResponseModel,
    PostTeacherRequestModel,
    PostTeacherResponseModel,
)

router = APIRouter(
    prefix="/users/teachers",
    tags=["teacher"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


@router.get(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListTeachersResponseModel,
)
def list_teachers(common_paginations: common_page_params):
    response_body = list_teachers_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


@router.post(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostTeacherResponseModel,
)
def post_teacher(request_body: PostTeacherRequestModel):
    response_body = post_teacher_request(request_body)
    return response_body


@router.get(
    "/{teacher_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetTeacherResponseModel,
)
def get_teacher(teacher_id: str):
    response_body = get_teacher_response(teacher_id)
    return response_body
