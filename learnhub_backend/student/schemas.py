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
