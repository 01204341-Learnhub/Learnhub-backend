from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import query_list_programs, query_list_lessons, query_get_lesson
from .schemas import (
    ListProgramsResponseModel,
    ListProgramsCourseModelBody,
    ListProgramsClassModelBody,
    ListLessonsResponseModel,
    ListLessonsModelBody,
    GetLessonResponseModel,
)


# lesson
def list_programs_response(skip: int = 0, limit: int = 0) -> ListProgramsResponseModel:
    queried_programs = query_list_programs(skip, limit)
    ta = TypeAdapter(
        list[Union[ListProgramsClassModelBody, ListProgramsCourseModelBody]]
    )
    response_body = ListProgramsResponseModel(
        programs=ta.validate_python(queried_programs)
    )
    return response_body


def list_lessons_response(
    course_id: str, chapter_id: str, skip: int = 0, limit: int = 0
) -> ListLessonsResponseModel:
    quried_lessons = query_list_lessons(course_id, chapter_id, skip, limit)
    ta = TypeAdapter(list[ListLessonsModelBody])
    response_body = ListLessonsResponseModel(lessons=ta.validate_python(quried_lessons))
    return response_body


def get_lesson_response(lesson_id: str) -> GetLessonResponseModel | None:
    try:
        quried_lesson = query_get_lesson(lesson_id)
    except:
        return None
    if quried_lesson == None:
        return None
    response_body = GetLessonResponseModel(**quried_lesson)
    return response_body
