from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ...dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    add_course_request,
    list_course_chapters_response,
    add_course_chapter_request,
    get_course_chapter_response,
    edit_course_chapter_response,
    delete_course_chapter_response,
    delete_course_lesson_request,
    list_course_lessons_response,
    get_course_lesson_response,
    edit_course_lesson_request,
    add_course_lesson_request,
    list_courses_response,
)

from .schemas import (
    ListCoursesResponseModel,
    PostCourseRequestModel,
    PostCourseResponseModel,
    ListCourseChaptersResponseModel,
    PostCourseChapterRequestModel,
    PostCourseChapterResponseModel,
    GetCourseChapterResponseModel,
    PatchCourseChapterRequestModel,
    ListCourseLessonsResponseModel,
    PostCourseLessonRequestModel,
    PostCourseLessonResponseModel,
    GetCourseLessonResponseModel,
    PatchCourseLessonRequestModel,
)

router = APIRouter(
    prefix="/programs/courses",
    tags=["courses"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


# COURSE
@router.get(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListCoursesResponseModel,
)
def list_courses(common_paginations: common_page_params):
    response_body = list_courses_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


@router.post(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostCourseResponseModel,
)
def add_course(course_body: PostCourseRequestModel):
    response_body = add_course_request(course_body)
    return response_body


# CHAPTER
@router.get(
    "/{course_id}/chapters",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListCourseChaptersResponseModel,
)
def list_course_chapters(course_id: str, common_paginations: common_page_params):
    response_body = list_course_chapters_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
        course_id=course_id,
    )
    return response_body


@router.post(
    "/{course_id}/chapters",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostCourseChapterResponseModel,
)
def add_course_chapter(course_id: str, chapter_body: PostCourseChapterRequestModel):
    response_body = add_course_chapter_request(
        course_id=course_id, chapter_body=chapter_body
    )
    return response_body


@router.get(
    "/{course_id}/chapters/{chapter_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetCourseChapterResponseModel,
)
def get_course_chapter(chapter_id: str):
    response_body = get_course_chapter_response(chapter_id=chapter_id)
    return response_body


@router.patch(
    "/{course_id}/chapters/{chapter_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def edit_course_chapter(
    chapter_id: str, chapter_to_edit: PatchCourseChapterRequestModel
):
    response_body = edit_course_chapter_response(
        chapter_id=chapter_id, chapter_to_edit=chapter_to_edit
    )
    return response_body


@router.delete(
    "/{course_id}/chapters/{chapter_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def delete_course_chapter(chapter_id: str, course_id: str):
    response_body = delete_course_chapter_response(
        chapter_id=chapter_id, course_id=course_id
    )
    return response_body


# LESSON
@router.get(
    "/{course_id}/chapters/{chapter_id}/lessons",
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
    "/{course_id}/chapters/{chapter_id}/lessons",
    status_code=201,
    response_model=PostCourseLessonResponseModel,
    response_model_exclude_none=True,
)
def post_course_lesson(
    course_id: str, chapter_id: str, requestBody: PostCourseLessonRequestModel
):
    response_body = add_course_lesson_request(course_id, chapter_id, requestBody)
    return response_body


@router.get(
    "/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}",
    status_code=200,
    response_model=GetCourseLessonResponseModel,
    response_model_exclude_none=True,
)
def get_course_lesson(course_id: str, chapter_id: str, lesson_id: str):
    response_body = get_course_lesson_response(course_id, chapter_id, lesson_id)
    return response_body


@router.patch(
    "/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}",
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
    response_body = edit_course_lesson_request(
        course_id, chapter_id, lesson_id, requestBody
    )
    return response_body


@router.delete(
    "/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}",
    status_code=200,
    response_model=GenericOKResponse,
    response_model_exclude_none=True,
)
def delete_course_lesson(course_id: str, chapter_id: str, lesson_id: str):
    response_body = delete_course_lesson_request(course_id, chapter_id, lesson_id)
    return response_body
