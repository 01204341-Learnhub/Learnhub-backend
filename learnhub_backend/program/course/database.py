from pymongo.results import UpdateResult
from ..database import db_client
from bson.objectid import ObjectId
from .schemas import (
    PostCourseChaptersRequestModel,
    PatchCourseChapterRequestModel,
    PatchCourseLessonRequestModel,
    PostCourseLessonRequestModel,
)

from ...dependencies import Exception


def query_list_course_chapters(course_id: str, skip: int = 0, limit: int = 100) -> list:
    chapters_cursor = db_client.chapter_coll.find(
        {"course_id": ObjectId(course_id)}, skip=skip, limit=limit
    )
    chapters = []
    for chapter in chapters_cursor:
        chapter["chapter_id"] = str(chapter["_id"])
        chapters.append(chapter)
    return chapters


def create_course_chapter(course_id: str, chapter_body: PostCourseChaptersRequestModel):
    chapter_body_to_inserted = chapter_body.model_dump()
    chapter_body_to_inserted["course_id"] = ObjectId(course_id)
    chapter_body_to_inserted["description"] = chapter_body.description
    chapter_body_to_inserted["chapter_length"] = 0
    chapter_body_to_inserted["lesson_count"] = 0  # TODO: Check if need to change

    # No matching course
    valid_course_id_filter = {"_id": ObjectId(course_id)}
    result = db_client.course_coll.find_one(filter=valid_course_id_filter)
    if result == None:
        raise Exception.not_found

    response_chapter_num = (
        db_client.chapter_coll.find(
            {"course_id": ObjectId(course_id)}, {"chapter_num": True}
        )
        .sort([("chapter_num", -1)])
        .limit(1)
    )
    try:
        chapter_body_to_inserted["chapter_num"] = (
            response_chapter_num.next()["chapter_num"] + 1
        )
    except StopIteration:
        chapter_body_to_inserted["chapter_num"] = 1
    response = db_client.chapter_coll.insert_one(chapter_body_to_inserted)
    return response


def query_course_chapter(chapter_id: str):
    queried_chapter = db_client.chapter_coll.find_one({"_id": ObjectId(chapter_id)})
    if queried_chapter != None:
        queried_chapter["chapter_id"] = str(queried_chapter["_id"])
        queried_chapter["course_id"] = str(queried_chapter["course_id"])
    return queried_chapter


def edit_course_chapter(
    chapter_id: str, chapter_to_edit: PatchCourseChapterRequestModel
):
    # print(chapter_to_edit)
    filter_chapter = {"_id": ObjectId(chapter_id)}
    chapter_to_edit_2 = {"$set": chapter_to_edit.model_dump(exclude_unset=True)}
    response = db_client.chapter_coll.update_one(filter_chapter, chapter_to_edit_2)
    return response


def delete_course_chapter(chapter_id: str, course_id: str) -> int:
    chapter_delete_filter = {"_id": ObjectId(chapter_id)}
    delete_response = db_client.chapter_coll.find_one_and_delete(
        filter=chapter_delete_filter, projection={"chapter_num": True}
    )
    if delete_response == None:  # Deletion Failed.
        return 0
    chapter_num_threshold = delete_response["chapter_num"]
    chapter_update_filter = {
        "course_id": ObjectId(course_id),
        "chapter_num": {"$gt": chapter_num_threshold},
    }
    update_body = {"$inc": {"chapter_num": -1}}
    update_response = db_client.chapter_coll.update_many(
        filter=chapter_update_filter, update=update_body
    )

    lesson_delete_filter = {
        "course_id": ObjectId(course_id),
        "chapter_id": ObjectId(chapter_id),
    }
    delete_response = db_client.lesson_coll.delete_many(filter=lesson_delete_filter)
    return 1


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


def query_course_lesson(course_id: str, chapter_id: str, lesson_id: str) -> dict | None:
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
    # Check for valid course and chapter
    valid_course_filter = {"_id": ObjectId(course_id)}
    course_result = db_client.course_coll.find_one(filter=valid_course_filter)
    if course_result == None:
        raise Exception.not_found
    valid_chapter_filter = {"_id": ObjectId(chapter_id)}
    chapter_result = db_client.chapter_coll.find_one(filter=valid_chapter_filter)
    if chapter_result == None:
        raise Exception.not_found

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
) -> UpdateResult:
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
    return result


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
