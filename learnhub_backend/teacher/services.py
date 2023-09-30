from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    create_teacher,
    query_list_teachers,
    query_teacher,
)

from .schemas import (
    GetTeacherResponseModel,
    ListTeachersModelBody,
    ListTeachersResponseModel,
    PostTeacherRequestModel,
    PostTeacherResponseModel,
)


# TEACHERS
def list_teachers_response(skip: int = 0, limit: int = 0):
    queried_teachers = query_list_teachers(skip=skip, limit=limit)

    ta = TypeAdapter(list[ListTeachersModelBody])
    response_body = ListTeachersResponseModel(
        teachers=ta.validate_python(queried_teachers)
    )
    return response_body


def post_teacher_request(request: PostTeacherRequestModel) -> PostTeacherResponseModel:
    teacher_id = create_teacher(request)
    response_body = PostTeacherResponseModel(teacher_id=teacher_id)
    return response_body


def get_teacher_response(teacher_id: str) -> GetTeacherResponseModel:
    queried_teacher = query_teacher(teacher_id)
    response_body = GetTeacherResponseModel(**queried_teacher)
    return response_body
