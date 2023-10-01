from typing import Optional, Union
from pydantic import BaseModel, HttpUrl, validator


## STUDENTS
class GetStudentResponseModel(BaseModel):
    uid: str
    student_id: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl | None = None


class PostStudentRequestModel(BaseModel):
    uid: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl | None = None


class PostStudentResponseModel(BaseModel):
    student_id: str


class ListStudentsResponseModel(BaseModel):
    students: list[GetStudentResponseModel]


class PatchStudentRequestModel(BaseModel):
    username: str | None = None
    fullname: str | None = None
    profile_pic: HttpUrl | None = None


# STUDENTS PROGRAMS
class TeacherModelBody(BaseModel):
    teacher_id: str
    teacher_name: str
    profile_pic: HttpUrl


class ListStudentCoursesModelBody(BaseModel):
    course_id: str
    course_pic: HttpUrl
    name: str
    status: str  # finished | not started | started
    teacher: TeacherModelBody
    progress: float
    rating: float


class ListStudentCourseResponseModel(BaseModel):
    courses: list[ListStudentCoursesModelBody]


# STUDENT COURSE PROGRESS
class LessonProgressModelBody(BaseModel):
    lesson_id: str
    chapter_id: str
    finished: bool
    lesson_completed: int
    # TODO: Add quiz score
    # quiz_score: int | None = None


class GetStudentCourseProgressResponseModel(BaseModel):
    progress: float
    lessons: list[LessonProgressModelBody]


# STUDENT CONFIG
class GetStudentConfigResponseModel(BaseModel):
    theme: str


class PatchStudentConfigRequestModel(BaseModel):
    theme: str | None = None


# PAYMENT METHOD
class GetStudentPaymentMethodResponseModel(BaseModel):
    payment_method_id: str
    name: str
    type: str
    card_number: str
    cvc: str
    expiration_date: str
    holder_fullname: str


class ListStudentPaymentMethodsResponseModel(BaseModel):
    payment_methods: list[GetStudentPaymentMethodResponseModel]


class PostStudentPaymentMethodRequestModel(BaseModel):
    name: str
    type: str
    card_number: str
    cvc: str
    expiration_date: str
    holder_fullname: str


class PostStudentPaymentMethodResponseModel(BaseModel):
    payment_method_id: str


class PatchStudentPaymentMethodRequestModel(BaseModel):
    name: str | None = None
    type: str | None = None
    card_number: str | None = None
    cvc: str | None = None
    expiration_date: str | None = None
    holder_fullname: str | None = None


# BASKET
class GetStudentBasketItemResponseModel(BaseModel):
    basket_item_id: str
    name: str
    type: str
    price: float
    program_id: str


class ListStudentBasketResponseModel(BaseModel):
    basket: list[GetStudentBasketItemResponseModel]


class PostStudentBasketItemRequestModel(BaseModel):
    program_id: str
    type: str


class PostStudentBasketItemResponseModel(BaseModel):
    basket_item_id: str
