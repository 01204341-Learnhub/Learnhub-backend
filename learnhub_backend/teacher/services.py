from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    query_list_teachers
)

from .schemas import (
    ListTeachersModelBody,
    ListTeachersResponseModel,
)


# TEACHERS
def list_teachers_response(skip: int = 0, limit: int = 0):
    queried_teachers = query_list_teachers(skip=skip, limit=limit)

    ta = TypeAdapter(list[ListTeachersModelBody])
    response_body = ListTeachersResponseModel(
        teachers=ta.validate_python(queried_teachers)
    )
    return response_body

