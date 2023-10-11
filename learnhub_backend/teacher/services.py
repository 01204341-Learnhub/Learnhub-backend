from pydantic import TypeAdapter
from typing import Annotated, Union
from pydantic import HttpUrl, TypeAdapter

from learnhub_backend.dependencies import GenericOKResponse

from .database import (
    create_teacher,
    create_teacher_payment_method,
    edit_teacher,
    edit_teacher_payment_method,
    query_class_by_teacher,
    query_course_by_teacher,
    query_list_teachers,
    query_teacher,
    remove_teacher_payment_method,
)

from .schemas import (
    ClassSchedule,
    GetTeacherPaymentMethodResponseModel,
    GetTeacherResponseModel,
    ListTeacherClassesModelBody,
    ListTeacherClassesResponseModel,
    ListTeacherCoursesModelBody,
    ListTeacherCoursesResponseModel,
    ListTeacherPaymentMethodsResponseModel,
    ListTeachersModelBody,
    ListTeachersResponseModel,
    PatchTeacherPaymentMethodRequestModel,
    PatchTeacherRequestModel,
    PostTeacherPaymentMethodRequestModel,
    PostTeacherPaymentMethodResponseModel,
    PostTeacherRequestModel,
    PostTeacherResponseModel,
)

from ..dependencies import (
    Exception,
    get_timestamp_from_datetime,
    mongo_datetime_to_timestamp,
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


def patch_teacher_request(teacher_id: str, request: PatchTeacherRequestModel):
    edit_teacher(teacher_id, request)
    return GenericOKResponse


# PROGRAM
def list_teacher_courses_response(teacher_id: str) -> ListTeacherCoursesResponseModel:
    courses_cur = query_course_by_teacher(teacher_id)
    courses = []
    for course_ in courses_cur:
        courses.append(
            ListTeacherCoursesModelBody(
                course_id=str(course_["_id"]),
                course_pic=course_["course_pic"],
                name=course_["name"],
                rating=course_["rating"],
                student_count=course_["student_count"],
            )
        )

    return ListTeacherCoursesResponseModel(courses=courses)


def list_teacher_classes_response(teacher_id: str) -> ListTeacherClassesResponseModel:
    classes_cur = query_class_by_teacher(teacher_id)
    classes = []
    for class_ in classes_cur:
        classes.append(
            ListTeacherClassesModelBody(
                class_id=str(class_["_id"]),
                name=class_["name"],
                class_pic=HttpUrl(class_["class_pic"]),
                status=class_["status"],
                registration_ended_date=get_timestamp_from_datetime(
                    class_["registration_ended_date"]
                ),
                class_ended_date=get_timestamp_from_datetime(
                    class_["class_ended_date"]
                ),
                student_count=class_["student_count"],
                max_student=class_["max_student"],
                schedules=[
                    ClassSchedule(
                        start=mongo_datetime_to_timestamp(_sched["start"]),
                        end=mongo_datetime_to_timestamp(_sched["end"]),
                    )
                    for _sched in class_["schedules"]
                ],
            )
        )

    return ListTeacherClassesResponseModel(classes=classes)


# PAYMENT METHOD
def list_teacher_payment_methods_response(
    teacher_id: str,
) -> ListTeacherPaymentMethodsResponseModel:
    teacher = query_teacher(teacher_id)
    if teacher == None:
        raise Exception.not_found
    payment_methods = teacher["payment_methods"]
    for i, method in enumerate(payment_methods):
        payment_methods[i]["payment_method_id"] = str(method["payment_method_id"])

    ta = TypeAdapter(list[GetTeacherPaymentMethodResponseModel])
    response_body = ListTeacherPaymentMethodsResponseModel(
        payment_methods=ta.validate_python(payment_methods)
    )

    return response_body


def get_teacher_payment_method_response(
    teacher_id: str, payment_method_id: str
) -> GetTeacherPaymentMethodResponseModel:
    teacher = query_teacher(teacher_id)
    if teacher == None:
        raise Exception.not_found

    response_method = {}
    for method in teacher["payment_methods"]:
        if str(method["payment_method_id"]) == payment_method_id:
            response_method = method
            response_method["payment_method_id"] = str(
                response_method["payment_method_id"]
            )
    if len(response_method) == 0:
        raise Exception.not_found
    response_body = GetTeacherPaymentMethodResponseModel(**response_method)

    return response_body


def post_teacher_payment_method_request(
    teacher_id: str, request: PostTeacherPaymentMethodRequestModel
) -> PostTeacherPaymentMethodResponseModel:
    oid = create_teacher_payment_method(teacher_id, request)
    response_body = PostTeacherPaymentMethodResponseModel(payment_method_id=oid)
    return response_body


def patch_teacher_payment_method_request(
    teacher_id: str,
    payment_method_id: str,
    request: PatchTeacherPaymentMethodRequestModel,
):
    edit_teacher_payment_method(teacher_id, payment_method_id, request)
    return GenericOKResponse


def delete_teacher_payment_method_request(
    teacher_id: str,
    payment_method_id: str,
):
    remove_teacher_payment_method(teacher_id, payment_method_id)
    return GenericOKResponse
