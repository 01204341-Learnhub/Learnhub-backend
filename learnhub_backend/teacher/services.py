from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import create_teacher, query_list_teachers

from .schemas import (
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
