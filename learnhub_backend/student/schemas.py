from typing import Optional, Union
from pydantic import BaseModel, HttpUrl, validator


# CLASS
class ClassInfoModelBody(BaseModel):
    class_id: str
    class_name: str


class ClassScheduleModelBody(BaseModel):
    start: int
    end: int


class SubmissionModelBody(BaseModel):
    submission_status: str  # check | uncheck | unsubmit
    submission_date: int


# TEACHER
class TeacherModelBody(BaseModel):
    teacher_id: str
    teacher_name: str
    profile_pic: HttpUrl


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


# COURSE
class ListStudentCoursesModelBody(BaseModel):
    course_id: str
    course_pic: HttpUrl
    name: str
    teacher: TeacherModelBody
    progress: float
    rating: float


class ListStudentCourseResponseModel(BaseModel):
    courses: list[ListStudentCoursesModelBody]


class courseChapterModelBody(BaseModel):
    chapter_num: int
    name: str
    chapter_id: str


class courseAnnouncementModelBody(BaseModel):
    announcement_id: str
    name: str
    last_edit: int


class GetStudentCourseResponseModel(BaseModel):
    course_pic: HttpUrl
    name: str
    teacher: TeacherModelBody
    chapters: list[courseChapterModelBody]
    announcements: list[courseAnnouncementModelBody]


# CLASS
class ListStudentClassModelBody(BaseModel):
    class_id: str
    name: str
    class_pic: HttpUrl
    status: str
    progress: float
    class_ended_date: int
    teacher: TeacherModelBody


class ListStudentClassResponseModel(BaseModel):
    classes: list[ListStudentClassModelBody]


class ListStudentClassAssignmentsModelBody(BaseModel):
    name: str
    class_info: ClassInfoModelBody
    group_name: str
    status: str  # open | closed
    submission: SubmissionModelBody


class ListStudentClassAssignmentsResponseModel(BaseModel):
    assignments: list[ListStudentClassAssignmentsModelBody]


# STUDENT COURSE PROGRESS
class LessonProgressModelBody(BaseModel):
    lesson_id: str
    chapter_id: str
    finished: bool
    lesson_completed: int


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
    program_id: str
    teacher: TeacherModelBody
    program_pic: HttpUrl
    rating: float
    review_count: int
    total_video_length: int | None = None
    difficulty_level: str
    price: float


class ListStudentBasketResponseModel(BaseModel):
    basket: list[GetStudentBasketItemResponseModel]


class PostStudentBasketItemRequestModel(BaseModel):
    program_id: str
    type: str


class PostStudentBasketItemResponseModel(BaseModel):
    basket_item_id: str
