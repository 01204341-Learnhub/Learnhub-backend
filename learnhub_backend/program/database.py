from ..database import db_client
from bson import ObjectId


def query_list_programs(skip: int = 0, limit: int = 100) -> list:
    courses_cursor = db_client.course_coll.find(skip=skip, limit=limit)
    programs = []
    for course in courses_cursor:
        course["course_id"] = str(course["_id"])
        course["type"] = "program"
        programs.append(course)
    # TODO: add class query

    return programs


def query_list_lessons(skip: int = 0, limit: int = 100) -> list:
    lessons_cursor = db_client.lesson_coll.find(skip=skip, limit=limit)
    lessons = []
    for lesson in lessons_cursor:
        lesson["lesson_id"] = str(lesson["_id"])
        lessons.append(lesson)

    return lessons


def query_get_lesson(lesson_id: str) -> dict | None:
    lesson_object_id = ObjectId(oid=lesson_id)
    lesson = db_client.lesson_coll.find_one({"_id": lesson_object_id})
    if lesson != None:
        lesson["lesson_id"] = str(lesson["_id"])
    return lesson
