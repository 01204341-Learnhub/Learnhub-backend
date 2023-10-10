from datetime import datetime
from typing import Annotated, Union
from bson.objectid import ObjectId
from pydantic import TypeAdapter
from pymongo.results import DeleteResult, UpdateResult

from learnhub_backend.dependencies import GenericOKResponse
from learnhub_backend.program.course.announcements.database import (
    list_course_announcement,
)
from learnhub_backend.program.course.database import query_list_course_chapters
from learnhub_backend.teacher.database import query_teacher

from .database import (
    create_student,
    create_student_basket_item,
    create_student_payment_method,
    edit_student,
    edit_student_payment_method,
    query_assignment,
    query_class,
    query_course,
    query_list_students,
    query_multiple_classes,
    query_student,
    query_student_assignment_submissions,
    query_student_basket,
    query_teacher_profile,
    remove_student,
    query_student_course_progress,
    edit_student_course_progress,
    edit_student_config,
    query_student_config,
    remove_student_basket_item,
    remove_student_payment_method,
)

from .schemas import (
    ClassInfoModelBody,
    GetStudentBasketItemResponseModel,
    GetStudentCourseResponseModel,
    GetStudentPaymentMethodResponseModel,
    ListStudentBasketResponseModel,
    ListStudentClassAssignmentsModelBody,
    ListStudentClassAssignmentsResponseModel,
    ListStudentClassModelBody,
    ListStudentClassResponseModel,
    ListStudentCourseResponseModel,
    ListStudentCoursesModelBody,
    ListStudentPaymentMethodsResponseModel,
    ListStudentsResponseModel,
    GetStudentResponseModel,
    PatchStudentPaymentMethodRequestModel,
    PostStudentBasketItemRequestModel,
    PostStudentBasketItemResponseModel,
    PostStudentPaymentMethodRequestModel,
    PostStudentPaymentMethodResponseModel,
    PostStudentRequestModel,
    PostStudentResponseModel,
    PatchStudentRequestModel,
    GetStudentCourseProgressResponseModel,
    LessonProgressModelBody,
    GetStudentConfigResponseModel,
    PatchStudentConfigRequestModel,
    SubmissionModelBody,
    TeacherModelBody,
    courseAnnouncementModelBody,
    courseChapterModelBody,
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


def get_student_response(student_id: str) -> GetStudentResponseModel:
    queried_student = query_student(student_id)
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


# PROGRAM
# STUDENT COURSE
def list_student_courses_response(student_id: str) -> ListStudentCourseResponseModel:
    student = query_student(student_id)
    student_id = str(student["_id"])
    student_courses = []
    for owned_program in student["owned_programs"]:
        if owned_program["type"] == "course":
            course = query_course(str(owned_program["program_id"]))
            teacher = query_teacher_profile(str(course["teacher_id"]))
            student_course_progress = query_student_course_progress(
                student_id, str(owned_program["program_id"])
            )

            total_lessons = (
                course["video_count"] + course["quiz_count"] + course["file_count"]
            )
            # assign value
            student_course = dict()
            student_course["course_id"] = str(course["_id"])
            student_course["course_pic"] = course["course_pic"]
            student_course["name"] = course["name"]
            student_course["teacher"] = TeacherModelBody(**teacher)
            student_course["rating"] = course["rating"]
            student_course["progress"] = (
                student_course_progress["finished_count"] * 100
            ) / total_lessons
            student_course = ListStudentCoursesModelBody(**student_course)
            student_courses.append(student_course)

    student_courses = ListStudentCourseResponseModel(courses=student_courses)
    return student_courses


def get_student_course_response(
    student_id: str, course_id: str
) -> GetStudentCourseResponseModel:
    student_course = dict()
    student_course["chapters"] = []
    student_course["announcements"] = []

    course = query_course(course_id)
    teacher = query_teacher_profile(str(course["teacher_id"]))

    course_chapters = query_list_course_chapters(course_id)
    for chapter in course_chapters:
        student_course["chapters"].append(
            courseChapterModelBody(
                chapter_num=chapter["chapter_num"],
                name=chapter["name"],
                chapter_id=str(chapter["_id"]),
            )
        )

    announcements = list_course_announcement(course_id)
    for announce in announcements:
        student_course["announcements"].append(
            courseAnnouncementModelBody(
                announcement_id=str(announce["_id"]),
                name=announce["name"],
                last_edit=announce["last_edit"],
            )
        )
    # response
    student_course["course_pic"] = course["course_pic"]
    student_course["name"] = course["name"]
    student_course["teacher"] = TeacherModelBody(**teacher)

    response = GetStudentCourseResponseModel(**student_course)
    return response


# STUDENT COURSE PROGRESS
def get_student_course_progress_response(
    student_id: str, course_id: str
) -> GetStudentCourseProgressResponseModel:
    response = dict()  # resposne_body
    response["lessons"] = []

    course = query_course(course_id)
    total_lessons = course["video_count"] + course["quiz_count"] + course["file_count"]

    progress = query_student_course_progress(student_id, course_id)

    for i, lesson in enumerate(progress["lessons"]):
        lesson_progress_body = {
            "lesson_id": str(lesson["lesson_id"]),
            "chapter_id": str(lesson["chapter_id"]),
            "finished": lesson["finished"],
            "lesson_completed": lesson["lesson_completed"],
        }
        response["lessons"].append(LessonProgressModelBody(**lesson_progress_body))

    response["progress"] = (progress["finished_count"] * 100) / total_lessons

    # response body
    response_body = GetStudentCourseProgressResponseModel(**response)
    return response_body


def patch_student_course_progress_request(
    student_id: str, course_id: str, requested_lesson: LessonProgressModelBody
) -> dict:
    # TODO: Validate response (not nessessary)
    response = edit_student_course_progress(
        student_id=student_id, course_id=course_id, requested_lesson=requested_lesson
    )
    return response


# STUDENT CLASS
def list_student_classes_response(student_id: str) -> ListStudentClassResponseModel:
    student = query_student(student_id)
    if student == None:
        raise Exception.not_found

    owned_programs = []
    for program_ in student["owned_programs"]:
        if program_["type"] == "class":
            owned_programs.append(str(program_["program_id"]))
    classes = query_multiple_classes(owned_programs)
    classes_response = []
    for class_ in classes:
        teacher = query_teacher_profile(str(class_["teacher_id"]))
        classes_response.append(
            ListStudentClassModelBody(
                class_id=str(class_["_id"]),
                name=class_["name"],
                class_pic=class_["class_pic"],
                status=class_["status"],
                progress=0,  # TODO: implement this
                class_ended_date=int(datetime.timestamp(class_["class_ended_date"])),
                teacher=TeacherModelBody(**teacher),
            )
        )

    response = ListStudentClassResponseModel(classes=classes_response)
    return response


def list_student_class_assignments_response(
    student_id: str,
) -> ListStudentClassAssignmentsResponseModel:
    submissions_cur = query_student_assignment_submissions(student_id)
    assignments_response = []
    for subm_ in submissions_cur:
        _cls = query_class(str(subm_["class_id"]))
        _assign_ = query_assignment(str(subm_["assignment_id"]))
        assignments_response.append(
            ListStudentClassAssignmentsModelBody(
                name=_assign_["name"],
                group_name=_assign_["group_name"],
                status=_assign_["status"],
                class_info=ClassInfoModelBody(
                    class_id=str(subm_["class_id"]),
                    class_name=_cls["name"],
                ),
                submission=SubmissionModelBody(
                    submission_status=subm_["status"],
                    submission_date=int(datetime.timestamp(subm_["submission_date"])),
                ),
            )
        )
    return ListStudentClassAssignmentsResponseModel(assignments=assignments_response)


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


# BASKET
def list_student_basket_response(student_id: str) -> ListStudentBasketResponseModel:
    basket = query_student_basket(student_id)
    for i, item in enumerate(basket):
        if item["type"] == "course":
            course = query_course(item["program_id"])
            basket[i]["name"] = course["name"]
            basket[i]["type"] = "course"
            basket[i]["teacher"] = query_teacher_profile(str(course["teacher_id"]))
            basket[i]["program_pic"] = course["course_pic"]
            basket[i]["rating"] = course["rating"]
            basket[i]["review_count"] = course["review_count"]
            basket[i]["total_video_length"] = course["total_video_length"]
            basket[i]["difficulty_level"] = course["difficulty_level"]
            basket[i]["price"] = course["price"]

        elif item["type"] == "class":
            cls = query_class(item["program_id"])
            basket[i]["name"] = cls["name"]
            basket[i]["type"] = "class"
            basket[i]["teacher"] = query_teacher_profile(str(cls["teacher_id"]))
            basket[i]["program_pic"] = cls["class_pic"]
            basket[i]["rating"] = cls["rating"]
            basket[i]["review_count"] = cls["review_count"]
            basket[i]["difficulty_level"] = cls["difficulty_level"]
            basket[i]["price"] = cls["price"]

    ta = TypeAdapter(list[GetStudentBasketItemResponseModel])
    response = ListStudentBasketResponseModel(basket=ta.validate_python(basket))
    return response


def get_student_basket_item_response(
    student_id: str, basket_item_id: str
) -> GetStudentBasketItemResponseModel:
    student = query_student(student_id)
    basket_item = dict()
    for item in student["basket"]:
        if item["basket_item_id"] == ObjectId(basket_item_id):
            basket_item = item
    if len(basket_item) == 0:
        raise Exception.not_found

    basket_item["basket_item_id"] = str(basket_item["basket_item_id"])
    basket_item["program_id"] = str(basket_item["program_id"])
    if basket_item["type"] == "course":
        course = query_course(basket_item["program_id"])
        basket_item["name"] = course["name"]
        basket_item["type"] = "course"
        basket_item["teacher"] = query_teacher_profile(str(course["teacher_id"]))
        basket_item["program_pic"] = course["course_pic"]
        basket_item["rating"] = course["rating"]
        basket_item["review_count"] = course["review_count"]
        basket_item["total_video_length"] = course["total_video_length"]
        basket_item["difficulty_level"] = course["difficulty_level"]
        basket_item["price"] = course["price"]
    elif basket_item["type"] == "class":
        cls = query_class(basket_item["program_id"])
        basket_item["name"] = cls["name"]
        basket_item["type"] = "class"
        basket_item["teacher"] = query_teacher_profile(str(cls["teacher_id"]))
        basket_item["program_pic"] = cls["class_pic"]
        basket_item["rating"] = cls["rating"]
        basket_item["review_count"] = cls["review_count"]
        basket_item["difficulty_level"] = cls["difficulty_level"]
        basket_item["price"] = cls["price"]

    return GetStudentBasketItemResponseModel(**basket_item)


def post_student_basket_item_request(
    student_id: str, request: PostStudentBasketItemRequestModel
) -> PostStudentBasketItemResponseModel:
    basket_item_id = create_student_basket_item(student_id, request)
    response = PostStudentBasketItemResponseModel(basket_item_id=basket_item_id)
    return response


def delete_student_basket_item_request(student_id: str, basket_item_id: str):
    remove_student_basket_item(student_id, basket_item_id)
    return GenericOKResponse
