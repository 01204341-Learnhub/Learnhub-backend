from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    query_list_programs,
    query_list_course_chapters,
    query_add_course_chapter,
    query_find_course_chapter,
)
from .schemas import (
    ListCourseChaptersModelBody,
    ListCourseChaptersResponseModel,
    AddCourseChaptersModel_in,
    GetCourseChapterResponseModel,
)
from .database import query_list_programs
from .schemas import (
    ListProgramsResponseModel,
    ListProgramsCourseModel,
    ListProgramsClassModel,
)


def list_programs_response(skip: int = 0, limit: int = 0) -> ListProgramsResponseModel:
    queried_programs = query_list_programs(skip, limit)
    ta = TypeAdapter(
        list[Union[ListProgramsClassModel, ListProgramsCourseModel]]
    )
    response_body = ListProgramsResponseModel(
        programs=ta.validate_python(queried_programs)
    )
    return response_body


def list_course_chapters_response(course_id: str = None, skip: int = 0, limit: int = 0):
    queried_chapters = query_list_course_chapters(
        course_id=course_id, skip=skip, limit=limit
    )
    ta = TypeAdapter(list[ListCourseChaptersModelBody])
    response_body = ListCourseChaptersResponseModel(
        chapters=ta.validate_python(queried_chapters)
    )
    return response_body


def add_course_chapter_response(
    course_id: str, chapter_body: AddCourseChaptersModel_in
) -> dict:
    response = query_add_course_chapter(course_id=course_id, chapter_body=chapter_body)
    return response


def get_course_chapter_response(chapter_id: str):
    queried_chapter = query_find_course_chapter(chapter_id=chapter_id)
    ta = TypeAdapter(GetCourseChapterResponseModel)
    response_body = GetCourseChapterResponseModel(
        **ta.validate_python(queried_chapter).model_dump()
    )
    return response_body

def edit_course_chapter_response(chapter_id=chapter_id):
    return
