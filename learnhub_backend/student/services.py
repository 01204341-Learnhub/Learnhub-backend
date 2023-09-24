from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import DeleteResult, UpdateResult

from .database import (
    edit_student,
    query_list_students,
    query_student,
    remove_student,
    query_student_course_progress,
    edit_student_course_progress,
    edit_student_config,
    query_student_config
)

from .schemas import (
    ListStudentsResponseModel,
    GetStudentResponseModel,
    PatchStudentRequestModel,
    GetStudentCourseProgressResponseModel,
    LessonProgressModelBody,
    PatchStudentConfigRequestModel,
    GetStudentConfigResponseModel,
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


def edit_student_request(
    student_id: str, request: PatchStudentRequestModel
) -> UpdateResult:
    result = edit_student(student_id, request)
    return result


def delete_student_request(student_id: str) -> DeleteResult:
    result = remove_student(student_id)
    return result


# STUDENT COURSE PROGRESS
def get_student_course_progress_response(
    student_id: str, course_id: str
) -> GetStudentCourseProgressResponseModel:
    queried_course_progress = query_student_course_progress(
        student_id=student_id, course_id=course_id
    )
    # response_body = GetStudentCourseProgressResponseModel(**queried_course_progress)
    ta = TypeAdapter(list[LessonProgressModelBody])
    response_body = GetStudentCourseProgressResponseModel(
        progress=queried_course_progress["progress"],
        lessons=ta.validate_python(queried_course_progress["lessons"]),
    )
    return response_body


def patch_student_course_progress_request(
    student_id: str, course_id: str, requested_lesson: LessonProgressModelBody
) -> dict:
    # TODO: Validate response (not nessessary)
    response  = edit_student_course_progress(student_id = student_id, course_id = course_id, requested_lesson = requested_lesson )
    return response

# STUDENT CONFIG
def edit_student_config_request(
    student_id: str, request: PatchStudentConfigRequestModel
) -> UpdateResult:
    result = edit_student_config(student_id, request)
    return result

def get_student_config_response(student_id: str) -> GetStudentConfigResponseModel | None:
    queried_student_config = query_student_config(student_id)
    try:
        queried_student_config = query_student_config(student_id)
    except:
        return None
    if queried_student_config == None:
        return None
    response_body = GetStudentConfigResponseModel(**queried_student_config)

    return response_body