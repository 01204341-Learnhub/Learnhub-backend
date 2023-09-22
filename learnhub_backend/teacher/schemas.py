from typing import Optional, Union
from pydantic import BaseModel, HttpUrl


# TEACHERS
class ListTeachersModelBody(BaseModel):
    teacher_id: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl


class ListTeachersResponseModel(BaseModel):
    teachers: list[ListTeachersModelBody]

