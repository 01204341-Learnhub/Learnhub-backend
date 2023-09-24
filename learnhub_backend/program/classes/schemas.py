from typing import Optional, Union
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from bson import ObjectId

class placeholder(BaseModel):
    pass

# CLASSES
class TeacherModelBody(BaseModel):
    teacher_id: str
    teacher_name: str
class TagModelBody(BaseModel):
    tag_id: str
    tag_name: str
class ListClassesModelBody(BaseModel):
    class_id: str
    name: str
    class_pic: HttpUrl
    teacher: str #TODO: change to TeacherModelBody
    status: str
    tags: list[str] #TODO: change to list[TagModelBody]
    registration_ended_date: datetime
    price: float

class ListClassesResponseModel(BaseModel):
    classes: list[ListClassesModelBody]
