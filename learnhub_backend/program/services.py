from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    query_list_programs,
    query_list_course_chapters,
    query_add_course_chapter,
    query_find_course_chapter,
    query_edit_course_chapter,
    query_delete_course_chapter,
)
from .schemas import (
    ListCourseChaptersModelBody,
    ListCourseChaptersResponseModel,
    AddCourseChaptersRequestModel,
    GetCourseChapterResponseModel,
    EditCourseChapterRequestModel,
)
from .database import query_list_programs
from .schemas import (
    ListProgramsResponseModel,
    ListProgramsCourseModelBody,
    ListProgramsClassModelBody,
)


def list_programs_response(skip: int = 0, limit: int = 0) -> ListProgramsResponseModel:
    queried_programs = query_list_programs(skip, limit)
    ta = TypeAdapter(
        list[Union[ListProgramsClassModelBody, ListProgramsCourseModelBody]]
    )
    response_body = ListProgramsResponseModel(
        programs=ta.validate_python(queried_programs)
    )
    return response_body


def list_course_chapters_response(course_id: str, skip: int = 0, limit: int = 0):
    queried_chapters = query_list_course_chapters(
        course_id=course_id, skip=skip, limit=limit
    )
    ta = TypeAdapter(list[ListCourseChaptersModelBody])
    response_body = ListCourseChaptersResponseModel(
        chapters=ta.validate_python(queried_chapters)
    )
    return response_body


def add_course_chapter_response(
    course_id: str, chapter_body: AddCourseChaptersRequestModel
) -> dict:
    response = query_add_course_chapter(course_id=course_id, chapter_body=chapter_body)
    if response.inserted_id == None:
        return None
    return {"chapter_id": str(response.inserted_id)}


def get_course_chapter_response(chapter_id: str):
    queried_chapter = query_find_course_chapter(chapter_id=chapter_id)
    if queried_chapter == None:
        return None
    ta = TypeAdapter(GetCourseChapterResponseModel)
    response_body = GetCourseChapterResponseModel(
        **ta.validate_python(queried_chapter).model_dump()
    )
    return response_body

def edit_course_chapter_response(chapter_id: str, chapter_to_edit: EditCourseChapterRequestModel):
    response = query_edit_course_chapter(chapter_id=chapter_id,chapter_to_edit=chapter_to_edit)
    return response

def delete_course_chapter_response(chapter_id: str,course_id:str)->int:
    response = query_delete_course_chapter(chapter_id=chapter_id , course_id = course_id)
    return response 

