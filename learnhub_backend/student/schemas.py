from typing import Optional, Union
from pydantic import BaseModel, HttpUrl


## STUDENTS
class GetStudentResponseModel(BaseModel):
    student_id: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl


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
