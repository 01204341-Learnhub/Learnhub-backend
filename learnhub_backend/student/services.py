from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import DeleteResult, UpdateResult

from learnhub_backend.dependencies import GenericOKResponse

from .database import (
    create_student,
    create_student_payment_method,
    edit_student,
    edit_student_payment_method,
    query_list_students,
    query_student,
    remove_student,
    query_student_course_progress,
    edit_student_course_progress,
    edit_student_config,
    query_student_config,
    remove_student_payment_method,
)

from .schemas import (
    GetStudentPaymentMethodResponseModel,
    ListStudentPaymentMethodsResponseModel,
    ListStudentsResponseModel,
    GetStudentResponseModel,
    PatchStudentPaymentMethodRequestModel,
    PostStudentPaymentMethodRequestModel,
    PostStudentPaymentMethodResponseModel,
    PostStudentRequestModel,
    PostStudentResponseModel,
    PatchStudentRequestModel,
    GetStudentCourseProgressResponseModel,
    LessonProgressModelBody,
    GetStudentConfigResponseModel,
    PatchStudentConfigRequestModel,
)

from ..dependencies import Exception


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


def post_student_request(request: PostStudentRequestModel) -> PostStudentResponseModel:
    student_id = create_student(request)
    response_body = PostStudentResponseModel(student_id=student_id)
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
    response = edit_student_course_progress(
        student_id=student_id, course_id=course_id, requested_lesson=requested_lesson
    )
    return response


# STUDENT CONFIG
def get_student_config_response(student_id: str) -> GetStudentConfigResponseModel:
    student_config = query_student_config(student_id)

    response_body = GetStudentConfigResponseModel(
        theme=student_config["config"]["theme"]
    )

    return response_body


def edit_student_config_request(
    student_id: str, request: PatchStudentConfigRequestModel
):
    result = edit_student_config(student_id, request)
    if result.matched_count == 0:
        raise Exception.not_found
    return GenericOKResponse


# PAYMENT METHOD
def list_student_payment_methods_response(
    student_id: str,
) -> ListStudentPaymentMethodsResponseModel:
    student = query_student(student_id)
    if student == None:
        raise Exception.not_found
    payment_methods = student["payment_methods"]
    for i, method in enumerate(payment_methods):
        payment_methods[i]["payment_method_id"] = str(method["payment_method_id"])

    ta = TypeAdapter(list[GetStudentPaymentMethodResponseModel])
    response_body = ListStudentPaymentMethodsResponseModel(
        payment_methods=ta.validate_python(payment_methods)
    )

    return response_body


def get_student_payment_method_response(
    student_id: str, payment_method_id: str
) -> GetStudentPaymentMethodResponseModel:
    student = query_student(student_id)
    if student == None:
        raise Exception.not_found

    response_method = {}
    for method in student["payment_methods"]:
        if str(method["payment_method_id"]) == payment_method_id:
            response_method = method
            response_method["payment_method_id"] = str(
                response_method["payment_method_id"]
            )
    if len(response_method) == 0:
        raise Exception.not_found
    response_body = GetStudentPaymentMethodResponseModel(**response_method)

    return response_body


def post_student_payment_method_request(
    student_id: str, request: PostStudentPaymentMethodRequestModel
) -> PostStudentPaymentMethodResponseModel:
    oid = create_student_payment_method(student_id, request)
    response_body = PostStudentPaymentMethodResponseModel(payment_method_id=oid)
    return response_body


def patch_student_payment_method_request(
    student_id: str,
    payment_method_id: str,
    request: PatchStudentPaymentMethodRequestModel,
):
    edit_student_payment_method(student_id, payment_method_id, request)
    return GenericOKResponse


def delete_student_payment_method_request(
    student_id: str,
    payment_method_id: str,
):
    remove_student_payment_method(student_id, payment_method_id)
    return GenericOKResponse
