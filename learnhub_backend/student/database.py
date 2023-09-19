from ..database import db_client
from bson.objectid import ObjectId


def query_list_students(skip: int = 0, limit: int = 100) -> list:
    filter = {"type": "student"}
    students_cursor = db_client.user_coll.find(skip=skip, limit=limit, filter=filter)
    students = []
    for student in students_cursor:
        student["student_id"] = str(student["_id"])
        students.append(student)

    return students
