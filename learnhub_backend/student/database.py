from ..database import db_client
from bson.objectid import ObjectId

from .config import (
    student_type,
)


def query_list_students(skip: int = 0, limit: int = 100) -> list:
    filter = {"type": student_type}
    students_cursor = db_client.user_coll.find(skip=skip, limit=limit, filter=filter)
    students = []
    for student in students_cursor:
        student["student_id"] = str(student["_id"])
        students.append(student)

    return students


def query_student(student_id: str) -> dict | None:
    filter = {"_id": ObjectId(student_id), "type": student_type}
    student = db_client.user_coll.find_one(filter=filter)
    if student != None:
        student["student_id"] = str(student["_id"])
    return student
