from typing import Optional, Union
from pydantic import BaseModel, HttpUrl


## STUDENTS
class GetStudentResponseModel(BaseModel):
    uid: str
    student_id: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl | None


class PostStudentRequestModel(BaseModel):
    uid: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl | None


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
