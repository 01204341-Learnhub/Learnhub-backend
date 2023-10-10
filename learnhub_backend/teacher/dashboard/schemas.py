from typing import Optional, Union
from pydantic import BaseModel, HttpUrl, validator


# AUX
class TagModelBody(BaseModel):
    tag_id: str
    tag_name: str


# DASHBOARD
class GetTeacherDashboardCourseModelBody(BaseModel):
    course_id: str
    name: str
    course_pic: HttpUrl
    tags: list[TagModelBody]
    rating: float
    review_count: int
    price: float
    difficulty_level: str


class GetTeacherDashboardClassModelBody(BaseModel):
    class_id: str
    name: str
    class_pic: HttpUrl
    status: str
    registration_ended_date: int
    open_date: int
    class_ended_date: int
    price: float


class GetTeacherDashboard(BaseModel):
    courses: list[GetTeacherDashboardCourseModelBody]
    classes: list[GetTeacherDashboardClassModelBody]
