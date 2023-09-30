from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ..dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    list_students_response,
    get_student_response,
    post_student_request,
    delete_student_request,
    edit_student_request,
    get_student_course_progress_response,
    patch_student_course_progress_request,
    get_student_config_response,
    edit_student_config_request,
)

from .schemas import (
    GetStudentResponseModel,
    PostStudentRequestModel,
    PostStudentResponseModel,
    ListStudentsResponseModel,
    PatchStudentRequestModel,
    ListStudentCourseResponseModel,
    GetStudentCourseProgressResponseModel,
    LessonProgressModelBody,
    GetStudentConfigResponseModel,
    PatchStudentConfigRequestModel,
)


router = APIRouter(
    prefix="/users/students",
    tags=["student"],
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
    response_model=ListStudentsResponseModel,
)
def list_students(common_paginations: common_page_params):
    response_body = list_students_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


@router.post(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostStudentResponseModel,
)
def post_student(request_body: PostStudentRequestModel):
    response_body = post_student_request(request_body)
    return response_body


@router.get(
    "/{student_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetStudentResponseModel,
)
def get_student(student_id: str):
    response_body = get_student_response(student_id)
    if response_body == None:
        raise Exception.not_found

    return response_body


@router.patch(
    "/{student_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def edit_student(student_id: str, request_body: PatchStudentRequestModel):
    result = edit_student_request(student_id, request_body)
    if result.matched_count == 0:
        raise Exception.not_found
    return GenericOKResponse


@router.delete(
    "/{student_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def delete_student(student_id: str):
    result = delete_student_request(student_id)
    if result.deleted_count == 0:
        raise Exception.not_found
    return GenericOKResponse


# STUDENT PROGRAMS
@router.get(
    "/{student_id}/programs/courses",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListStudentCourseResponseModel,
)
def list_student_courses(student_id: str):
    # TODO:implement this
    pass


# STUDENT COURSE PROGRESS
@router.get(
    "/{student_id}/programs/courses/{course_id}/progress",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetStudentCourseProgressResponseModel,
)
def get_student_course_progress(student_id: str, course_id: str):
    response_body = get_student_course_progress_response(
        student_id=student_id, course_id=course_id
    )
    return response_body


@router.patch(
    "/{student_id}/programs/courses/{course_id}/progress",
    status_code=200,
    response_model_exclude_none=True,
    response_model=dict,
)
def patch_student_course_progress(
    student_id: str, course_id: str, request_body: LessonProgressModelBody
):
    response_body = patch_student_course_progress_request(
        student_id=student_id, course_id=course_id, requested_lesson=request_body
    )
    return response_body


# STUDENT CONFIG
@router.get(
    "/{student_id}/config",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetStudentConfigResponseModel,
)
def get_student_config(student_id: str):
    response_body = get_student_config_response(student_id=student_id)
    return response_body


@router.patch(
    "/{student_id}/config",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def edit_student_config(student_id: str, request_body: PatchStudentConfigRequestModel):
    response_body = edit_student_config_request(
        student_id=student_id, request=request_body
    )
    return response_body
