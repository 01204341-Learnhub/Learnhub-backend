from fastapi import APIRouter, Depends
from typing import Annotated, Union

from ..dependencies import common_pagination_parameters, GenericOKResponse
from .schemas import (
    ListProgramsResponseModel,
    GetCourseLessonResponseModel,
    ListCourseLessonsResponseModel,
    PatchCourseLessonRequestModel,
    PostCourseLessonRequestModel,
    PostCourseLessonResponseModel,
)
from .services import (
    delete_course_lesson_request,
    list_programs_response,
    list_course_lessons_response,
    get_course_lesson_response,
    patch_course_lesson_request,
    post_course_lesson_request,
)
from .exceptions import Exception


router = APIRouter(
    prefix="/programs",
    tags=["program"],
    dependencies=[Depends(common_pagination_parameters)],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


@router.get(
    "/",
    status_code=200,
    response_model=ListProgramsResponseModel,
    response_model_exclude_none=True,
)
def list_programs(common_paginations: common_page_params):
    response_body = list_programs_response(
        common_paginations["skip"], common_paginations["limit"]
    )
    return response_body


@router.get(
    "/courses/{course_id}/chapters/{chapter_id}/lessons",
    status_code=200,
    response_model=ListCourseLessonsResponseModel,
    response_model_exclude_none=True,
)
def list_course_lessons(
    course_id: str, chapter_id: str, common_paginations: common_page_params
):
    response_body = list_course_lessons_response(
        course_id, chapter_id, common_paginations["skip"], common_paginations["limit"]
    )
    return response_body


@router.post(
    "/courses/{course_id}/chapters/{chapter_id}/lessons",
    status_code=201,
    response_model=PostCourseLessonResponseModel,
    response_model_exclude_none=True,
)
def post_course_lesson(
    course_id: str, chapter_id: str, requestBody: PostCourseLessonRequestModel
):
    response_body = post_course_lesson_request(course_id, chapter_id, requestBody)
    return response_body


@router.get(
    "/courses/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}",
    status_code=200,
    response_model=GetCourseLessonResponseModel,
    response_model_exclude_none=True,
)
def get_course_lesson(course_id: str, chapter_id: str, lesson_id: str):
    response_body = get_course_lesson_response(course_id, chapter_id, lesson_id)
    if response_body == None:
        raise Exception.not_found
    return response_body


@router.patch(
    "/courses/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}",
    status_code=200,
    response_model=GenericOKResponse,
    response_model_exclude_none=True,
)
def patch_course_lesson(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
    requestBody: PatchCourseLessonRequestModel,
):
    modified_count = patch_course_lesson_request(
        course_id, chapter_id, lesson_id, requestBody
    )
    if modified_count < 1:
        raise Exception.bad_request
    response_body = GenericOKResponse()
    return response_body


@router.delete(
    "/courses/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}",
    status_code=200,
    response_model=GenericOKResponse,
    response_model_exclude_none=True,
)
def delete_course_lesson(course_id: str, chapter_id: str, lesson_id: str):
    delete_count = delete_course_lesson_request(course_id, chapter_id, lesson_id)
    if delete_count < 1:
        raise Exception.bad_request
    response_body = GenericOKResponse()
    return response_body
