from ..database import db_client
from bson import ObjectId
from .schemas import PatchCourseLessonRequestModel, PostCourseLessonRequestModel


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
        "chapter_id": ObjectId(chapter_id),
    }
    lesson = db_client.lesson_coll.find_one(filter=filter)
    if lesson != None:
        lesson["lesson_id"] = str(lesson["_id"])
    return lesson


def create_course_lesson(
    course_id: str, chapter_id: str, request: PostCourseLessonRequestModel
) -> str:
    body = {
        "course_id": ObjectId(course_id),
        "chapter_id": ObjectId(chapter_id),
        "name": request.name,
        "description": request.description,
        "lesson_type": "video",  # TODO: add utils to check for url type
        "src": str(request.src),
    }

    filter = {"course_id": ObjectId(course_id), "chapter_id": ObjectId(chapter_id)}
    while True:
        # Auto increment lesson_num
        cursor = (
            db_client.lesson_coll.find(filter, {"lesson_num": True})
            .sort([("lesson_num", -1)])
            .limit(1)
        )
        try:
            body["lesson_num"] = cursor.next()["lesson_num"] + 1
        except StopIteration:
            body["lesson_num"] = 1
        break

    object_id = db_client.lesson_coll.insert_one(body)
    return str(object_id.inserted_id)


def edit_course_lesson(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
    request: PatchCourseLessonRequestModel,
) -> int:
    filter = {
        "_id": ObjectId(lesson_id),
        "course_id": ObjectId(course_id),
        "chapter_id": ObjectId(chapter_id),
    }

    update_body = {}
    if request.name != None:
        update_body["name"] = request.name
    if request.description != None:
        update_body["description"] = request.description
    if request.src != None:
        update_body["src"] = str(request.src)
    update = {"$set": update_body}

    result = db_client.lesson_coll.update_one(filter=filter, update=update)
    return result.modified_count


def remove_course_lesson(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
) -> int:
    delete_filter = {
        "_id": ObjectId(lesson_id),
        "course_id": ObjectId(course_id),
        "chapter_id": ObjectId(chapter_id),
    }
    result = db_client.lesson_coll.find_one_and_delete(delete_filter)
    if result == None:  # Deletion Failed.
        return 0
    lesson_num_threshold = result["lesson_num"]

    update_filter = {
        "course_id": ObjectId(course_id),
        "chapter_id": ObjectId(chapter_id),
        "lesson_num": {"$gt": lesson_num_threshold},
    }

    update_body = {"$inc": {"lesson_num": -1}}
    db_client.lesson_coll.update_many(filter=update_filter, update=update_body)
    return 1
