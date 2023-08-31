from fastapi import APIRouter, Depends
from typing import Annotated, Union

from ..dependencies import common_pagination_parameters
from .schemas import (
    ListProgramsResponseModel,
    ListCourseChaptersResponseModel,
    AddCourseChaptersModel_in,
    GetCourseChapterResponseModel,
)
from .services import (
    list_programs_response,
    list_course_chapters_response,
    add_course_chapter_response,
    get_course_chapter_response,
)


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
    "/courses/{course_id}/chapters",
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
    "/courses/{course_id}/chapters",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListProgramsResponseModel,
)
def add_course_chapter(course_id: str, chapter_body: AddCourseChaptersModel_in) -> dict:
    response_body = add_course_chapter_response(
        course_id=course_id, chapter_body=chapter_body
    )
    return response_body


@router.get(
    "/courses/{course_id}/chapters/{chapter_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetCourseChapterResponseModel,
)
def get_course_chapter(chapter_id: str):
    response_body = get_course_chapter_response(chapter_id=chapter_id)
    return response_body

@router.patch(
    "/courses/{course_id}/chapters/{chapter_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=fixfixfixfixfix,
)
def edit_course_chapter(chapter_id: str):
    response_body = edit_course_chapter_response(chapter_id=chapter_id)
    return response_body
