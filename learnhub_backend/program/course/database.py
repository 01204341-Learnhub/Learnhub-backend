from ..database import db_client
from bson.objectid import ObjectId
from .schemas import (
    PostCourseChaptersRequestModel,
    PatchCourseChapterRequestModel,
    PatchCourseLessonRequestModel,
    PostCourseLessonRequestModel,
    PostCourseRequestModel,
    PatchCourseRequestModel,
)


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

def remove_course(
    course_id: str,
) -> int:
    delete_filter = {
        "course_id": ObjectId(course_id),
    }
    result = db_client.lesson_coll.find_one_and_delete(delete_filter)
    if result == None:  # Deletion Failed.
        return 0
    
    update_filter = {
        "course_id": ObjectId(course_id),   
    }
    update_body = {}
    db_client.lesson_coll.update_many(filter=update_filter,update=update_body)
    return 1

def edit_course(
    course_id: str,
    request: PatchCourseRequestModel,
) -> int:
    filter = {
        "course_id": ObjectId(course_id),
    }

    update_body = {}
    if request.name != None:
        update_body["name"] = request.name
    if request.course_pic != None:
        update_body["course_pic"] = str(request.course_pic)
    if request.description != None:
        update_body["description"] = request.description
    if request.course_objective != None:
        update_body["course_objective"] = request.course_objective
    if request.course_requirement != None:
        update_body["course_requirement"] = request.course_requirement
    if request.difficulty_level != None:
        update_body["difficulty_level"] = request.difficulty_level
    if request.price != None:
        update_body["price"] = request.price
    
    update = {"$set": update_body}

    result = db_client.lesson_coll.update_one(filter=filter, update=update)
    return result.modified_count

def create_course(
    course_id: str, request: PostCourseRequestModel
) -> str:
    body = {
        "name": request.name,
        "description": request.description,
        # "created_date": {
        #     "$date": "2022-12-31T17:00:00.000Z"
        # },
        "course_pic": str(request.course_pic),
        # "student_count": 1,
        # "rating": 0,
        # "review_count": 0,
        "price": request.price,
        "teacher_id": request.teacher_id,
        "course_objective": request.course_objective,
        "course_requirement": request.course_requirement,
        "difficulty_level": request.difficulty_level,
        # "tags": [
        #     {
        #     "$oid": "6509b76eda50b4eec1867261"
        #     },
        #     {
        #     "$oid": "6509b79bda50b4eec1867265"
        #     }
        # ],
        # "total_video_length": 600,
        # "chapter_count": 1,
        # "file_count": 1,
        # "quiz_count": 0,
        # "status": "started"

    }
    #not finnish
    filter = {"course_id": ObjectId(course_id),}
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

