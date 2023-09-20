from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    query_list_students,
    query_student,
)

from .schemas import (
    ListStudentsResponseModel,
    GetStudentResponseModel,
)


# STUDENTS
def list_students_response(skip: int = 0, limit: int = 0) -> ListStudentsResponseModel:
    queried_students = query_list_students(skip=skip, limit=limit)

    ta = TypeAdapter(list[GetStudentResponseModel])
    response_body = ListStudentsResponseModel(
        students=ta.validate_python(queried_students)
    )
    return response_body


def get_student_response(student_id: str) -> GetStudentResponseModel | None:
    queried_student = query_student(student_id)
    try:
        queried_student = query_student(student_id)
    except:
        return None
    if queried_student == None:
        return None
    response_body = GetStudentResponseModel(**queried_student)

    return response_body
