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


def query_student(student_id: str) -> dict | None:
    filter = {"_id": ObjectId(student_id), "type": student_type}
    student = db_client.user_coll.find_one(filter)
    return student


def query_teacher(teacher_id: str) -> dict | None:
    filter = {"_id": ObjectId(teacher_id), "type": teacher_type}
    teacher = db_client.user_coll.find_one(filter)
    return teacher


# CLASS
def query_class(class_id: str) -> dict | None:
    filter = {"_id": ObjectId(class_id)}
    _class = db_client.class_coll.find_one(filter)
    return _class


def query_assignments_by_class(class_id: str) -> Cursor:
    filter = {"class_id": ObjectId(class_id)}
    assignment_cur = db_client.assignment_coll.find(filter)
    return assignment_cur


def query_submission_by_assignment(assignment_id: str) -> dict | None:
    filter = {"assignment_id": ObjectId(assignment_id)}
    sub = db_client.assignment_submission_coll.find_one(filter)
    return sub


# COURSE
def query_course(course_id: str) -> dict | None:
    filter = {"_id": ObjectId(course_id)}
    _course = db_client.course_coll.find_one(filter)
    return _course


def query_announcements_by_course(course_id: str) -> Cursor:
    filter = {"course_id": ObjectId(course_id)}
    _announcements = db_client.announcement_coll.find(filter)
    return _announcements
