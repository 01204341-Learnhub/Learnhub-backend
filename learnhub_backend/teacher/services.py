from pydantic import TypeAdapter
from typing import Annotated, Union
from pydantic import HttpUrl, TypeAdapter

from learnhub_backend.dependencies import GenericOKResponse
from learnhub_backend.program.classes.database import query_class
from learnhub_backend.program.course.database import query_course
from learnhub_backend.student.database import query_student

from .database import (
    create_teacher,
    create_teacher_payment_method,
    edit_teacher,
    edit_teacher_payment_method,
    query_class_by_teacher,
    query_course_by_teacher,
    query_list_teachers,
    query_teacher,
    query_transaction_by_programs,
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
    ListTeacherIncomesModelBody,
    ListTeacherIncomesResponseModel,
    ListTeacherPaymentMethodsResponseModel,
    ListTeachersModelBody,
    ListTeachersResponseModel,
    PatchTeacherPaymentMethodRequestModel,
    PatchTeacherRequestModel,
    PostTeacherPaymentMethodRequestModel,
    PostTeacherPaymentMethodResponseModel,
    PostTeacherRequestModel,
    PostTeacherResponseModel,
    StudentModelBody,
)

from .dependencies import (
    _Program,
)
from ..dependencies import (
    Exception,
    get_timestamp_from_datetime,
    mongo_datetime_to_timestamp,
    course_type,
    class_type,
    student_type,
    teacher_type,
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


# INCOMES
def list_teacher_incomes_response(teacher_id: str) -> ListTeacherIncomesResponseModel:
    teacher = query_teacher(teacher_id)
    programs: list[_Program] = []
    for program_ in teacher["owned_programs"]:
        programs.append(_Program(str(program_["program_id"]), program_["type"]))
    transaction_cur = query_transaction_by_programs(programs)

    incomes: list[ListTeacherIncomesModelBody] = []

    program_ids = {str(program_.program_id) for program_ in programs}

    for transaction_ in transaction_cur:
        student = query_student(str(transaction_["user_id"]))
        for purchase_ in transaction_["purchase_list"]:
            if str(purchase_["program_id"]) in program_ids:
                if purchase_["type"] == course_type:
                    course = query_course(str(purchase_["program_id"]))
                    if course == None:
                        raise Exception.not_found
                    incomes.append(
                        ListTeacherIncomesModelBody(
                            type=purchase_["type"],
                            program_id=str(purchase_["program_id"]),
                            program_pic=HttpUrl(course["course_pic"]),
                            name=course["name"],
                            buyer=StudentModelBody(
                                student_id=str(student["_id"]),
                                student_name=student["fullname"],
                            ),
                            price=course["price"],
                        )
                    )
                elif purchase_["type"] == class_type:
                    class_ = query_class(str(purchase_["program_id"]))
                    if class_ == None:
                        raise Exception.not_found
                    incomes.append(
                        ListTeacherIncomesModelBody(
                            type=purchase_["type"],
                            program_id=str(purchase_["program_id"]),
                            program_pic=HttpUrl(class_["class_pic"]),
                            name=class_["name"],
                            buyer=StudentModelBody(
                                student_id=str(student["_id"]),
                                student_name=student["fullname"],
                            ),
                            price=class_["price"],
                        )
                    )
    return ListTeacherIncomesResponseModel(incomes=incomes)


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
