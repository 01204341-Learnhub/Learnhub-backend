from typing import Annotated, Union
from pydantic import TypeAdapter
from pydantic_core.core_schema import ErrorType

from .database import (
                query_list_programs,
                query_list_lessons, query_get_lesson
                )
from .schemas import (
                ListProgramsModel, ListProgramsCourseModel, ListProgramsClassModel,
                ListLessonsModel, ListLessonsModelBody, GetLessonModel
                      )


# lesson
def list_programs_response(skip: int = 0, limit : int = 0) -> ListProgramsModel:
        queried_programs = query_list_programs(skip, limit)
        ta = TypeAdapter(list[Union[ListProgramsClassModel, ListProgramsCourseModel]])
        response_body = ListProgramsModel(programs=ta.validate_python(queried_programs))
        return response_body

def list_lessons_response(skip: int=0, limit : int =0)-> ListLessonsModel:
        quried_lessons = query_list_lessons(skip, limit)
        ta = TypeAdapter(list[ListLessonsModelBody])
        response_body = ListLessonsModel(lessons = ta.validate_python(quried_lessons))
        return response_body

def get_lesson_response(lesson_id : str) -> GetLessonModel | None : 
        quried_lesson = query_get_lesson(lesson_id)
        if quried_lesson == None:
                return None
        response_body = GetLessonModel(**quried_lesson)
        return response_body
