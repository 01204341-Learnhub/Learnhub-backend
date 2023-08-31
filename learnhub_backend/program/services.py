from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
                query_list_programs,
                query_list_lessons
                )
from .schemas import (
                ListProgramsModel, ListProgramsCourseModel, ListProgramsClassModel,
                ListLessonsModel, ListLessonsModelBody
                      )


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
