from ..database import db_client
from bson.objectid import ObjectId

# TEACHERS
def query_list_teachers(skip: int = 0, limit: int = 100) -> list:
    filter = {"type": "teacher"}
    teachers_cursor = db_client.user_coll.find(skip=skip, limit=limit, filter=filter)
    teachers = []
    for teacher in teachers_cursor:
        teacher["teacher_id"] = str(teacher["_id"])
        teachers.append(teacher)

    return teachers
