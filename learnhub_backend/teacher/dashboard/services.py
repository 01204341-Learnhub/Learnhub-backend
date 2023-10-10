from datetime import datetime, timezone, tzinfo
from typing import Annotated, Union
from bson.objectid import ObjectId
from pydantic import HttpUrl, TypeAdapter
from pymongo.results import DeleteResult, UpdateResult

from learnhub_backend.dependencies import (
    GenericOKResponse,
    Exception,
    class_type,
    course_type,
    student_type,
    teacher_type,
    get_timestamp_from_datetime,
)
from learnhub_backend.teacher.dashboard.database import (
    query_class_by_teacher_id,
    query_course_by_teacher_id,
)
from .schemas import (
    GetTeacherDashboardClassModelBody,
    GetTeacherDashboardCourseModelBody,
    GetTeacherDashboardResponseModel,
)

from .config import (
    _Program,
)


# DASHBOARD
def get_teacher_dashboard_response(teacher_id: str) -> GetTeacherDashboardResponseModel:
    courses: list[GetTeacherDashboardCourseModelBody] = []
    classes: list[GetTeacherDashboardClassModelBody] = []

    courses_cur = query_course_by_teacher_id(teacher_id)
    for course_ in courses_cur:
        courses.append(
            GetTeacherDashboardCourseModelBody(
                course_id=str(course_["_id"]),
                name=course_["name"],
                course_pic=HttpUrl(course_["course_pic"]),
                rating=course_["rating"],
                review_count=course_["review_count"],
                price=course_["price"],
                difficulty_level=course_["difficulty_level"],
            )
        )
    classes_cur = query_class_by_teacher_id(teacher_id)
    for class_ in classes_cur:
        classes.append(
            GetTeacherDashboardClassModelBody(
                class_id=str(class_["_id"]),
                name=class_["name"],
                class_pic=HttpUrl(class_["class_pic"]),
                status=class_["status"],
                registration_ended_date=get_timestamp_from_datetime(
                    class_["registration_ended_date"]
                ),
                open_date=get_timestamp_from_datetime(class_["open_date"]),
                class_ended_date=get_timestamp_from_datetime(
                    class_["class_ended_date"]
                ),
                price=class_["price"],
            )
        )

    return GetTeacherDashboardResponseModel(
        courses=courses,
        classes=classes,
    )
