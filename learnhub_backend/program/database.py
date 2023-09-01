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


def query_list_course_lessons(
    course_id: str, chapter_id: str, skip: int = 0, limit: int = 100
) -> list:
    filter = {"course_id": ObjectId(course_id), "chapter_id": ObjectId(chapter_id)}
    lessons_cursor = db_client.lesson_coll.find(filter=filter, skip=skip, limit=limit)
    lessons = []
    for lesson in lessons_cursor:
        lesson["lesson_id"] = str(lesson["_id"])
        lessons.append(lesson)

    return lessons


def query_get_course_lesson(
    course_id: str, chapter_id: str, lesson_id: str
) -> dict | None:
    filter = {
        "_id": ObjectId(lesson_id),
        "course_id": ObjectId(course_id),
        "chapter_id`": ObjectId(chapter_id),
    }
    lesson = db_client.lesson_coll.find_one(filter=filter)
    if lesson != None:
        lesson["lesson_id"] = str(lesson["_id"])
    return lesson
