from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ...dependencies import common_pagination_parameters, GenericOKResponse, Exception

from .services import (
    list_course_chapters_response,
    add_course_chapter_response,
    get_course_chapter_response,
    edit_course_chapter_response,
    delete_course_chapter_response,
    delete_course_lesson_request,
    list_course_lessons_response,
    get_course_lesson_response,
    edit_course_lesson_request,
    add_course_lesson_request,
)

from .schemas import (
    ListCourseResponseModel, #123
    ListCourseIdResponseModel, #123
    ListCourseStudentsResponseModel, #123
    PostCourseRequestModel, #123
    ListCourseChaptersResponseModel,
    PostCourseChaptersRequestModel,
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

#bun start here
@router.get(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListCourseResponseModel, #123
)
def list_course(common_paginations: common_page_params):
    response_body = list_course_response( #123
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
        
    )
    return response_body

@router.post(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=dict,
)
def add_course(chapter_body: PostCourseRequestModel): #123
    response_body = add_course_response( #123
        course_body=course_body    #123
    )
    if response_body == None:
        raise Exception.bad_request
    return response_body

@router.get(
    "/{course_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListCourseIdResponseModel, #123
)
def list_course(course_id: str, common_paginations: common_page_params):
    response_body = list_course_id_response( #123
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
        course_id=course_id,
    )
    return response_body

@router.get(
    "/{course_id}/students",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListCourseStudentsResponseModel, #123
)
def list_course(course_id: str, common_paginations: common_page_params):
    response_body = list_course_students_response( #123
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
        course_id=course_id,
    )
    return response_body


#bun end here

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
    response_model=dict,
)
def add_course_chapter(course_id: str, chapter_body: PostCourseChaptersRequestModel):
    response_body = add_course_chapter_response(
        course_id=course_id, chapter_body=chapter_body
    )
    if response_body == None:
        raise Exception.bad_request
    return response_body


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
    "/{course_id}/chapters/{chapter_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetCourseChapterResponseModel,
)
def get_course_chapter(chapter_id: str):
    response_body = get_course_chapter_response(chapter_id=chapter_id)
    if response_body == None:
        raise Exception.not_found
    return response_body


@router.get(
    "/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}",
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
    "/{course_id}/chapters/{chapter_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=dict,
)
def edit_course_chapter(
    chapter_id: str, chapter_to_edit: PatchCourseChapterRequestModel
):
    response_body = edit_course_chapter_response(
        chapter_id=chapter_id, chapter_to_edit=chapter_to_edit
    )
    if response_body.matched_count == 0:
        raise Exception.not_found
    elif response_body.modified_count == 0:
        return {"message": "OK but no change"}
    return {"message": "OK"}


@router.delete(
    "/{course_id}/chapters/{chapter_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=dict,
)
def delete_course_chapter(chapter_id: str, course_id: str):
    response_body = delete_course_chapter_response(
        chapter_id=chapter_id, course_id=course_id
    )
    if response_body == 0:
        raise Exception.bad_request
    return {"message": "OK"}


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
    modified_count = edit_course_lesson_request(
        course_id, chapter_id, lesson_id, requestBody
    )
    if modified_count < 1:
        raise Exception.bad_request
    response_body = GenericOKResponse()
    return response_body


@router.delete(
    "/{course_id}/chapters/{chapter_id}/lessons/{lesson_id}",
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