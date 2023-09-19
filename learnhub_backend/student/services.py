from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    query_list_students,
)

from .schemas import (
    ListStudentsResponseModel,
    ListStudentsModelBody,
)


# STUDENTS
def list_students_response(skip: int = 0, limit: int = 0):
    queried_students = query_list_students(skip=skip, limit=limit)

    ta = TypeAdapter(list[ListStudentsModelBody])
    response_body = ListStudentsResponseModel(
        students=ta.validate_python(queried_students)
    )
    return response_body
