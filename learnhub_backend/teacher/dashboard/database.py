from logging import error
from pymongo.cursor import Cursor
from pymongo.results import DeleteResult, UpdateResult
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ...database import db_client
from ...dependencies import (
    student_type,
    teacher_type,
    course_type,
    Exception,
)


def query_course_by_teacher_id(teacher_id: str) -> Cursor:
    filter = {"teacher_id": ObjectId(teacher_id)}
    courses_cur = db_client.course_coll.find(filter)
    return courses_cur


def query_class_by_teacher_id(teacher_id: str) -> Cursor:
    filter = {"teacher_id": ObjectId(teacher_id)}
    classes_cur = db_client.class_coll.find(filter)
    return classes_cur
