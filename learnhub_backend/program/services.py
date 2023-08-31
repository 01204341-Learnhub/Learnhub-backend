from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import query_list_programs
from .schemas import List_programs_model, List_programs_class_model, List_programs_course_model


def list_programs_response(skip: int = 0, limit : int = 0) -> List_programs_model:
        queried_programs = query_list_programs(skip, limit)
        ta = TypeAdapter(list[Union[List_programs_class_model, List_programs_course_model]])
        response_body = List_programs_model(programs=ta.validate_python(queried_programs))
        return response_body
