from datetime import datetime

from pymongo.results import InsertOneResult, UpdateResult
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..database import db_client

from .schemas import (
    PostCourseRequestModel,
    PostCourseChapterRequestModel,
    PatchCourseChapterRequestModel,
    PatchCourseLessonRequestModel,
    PostCourseLessonRequestModel,
)

from ...dependencies import (
    Exception,
    teacher_type,
)


# AUXILARY
def query_teacher_by_id(id: str | ObjectId):
    try:
        filter = {"type": teacher_type, "_id": id}
        if type(id) == str:
            filter["_id"] = ObjectId(id)
        teacher = db_client.user_coll.find_one(filter=filter)
        return teacher

    except InvalidId:
        raise Exception.bad_request


def query_list_tags_by_id(ids: list[str | ObjectId]):
    try:
        object_ids = list(map(ObjectId, ids))

        filter = {"_id": {"$in": object_ids}}
        tags = db_client.tag_coll.find(filter)
        return tags

    except InvalidId:
        raise Exception.bad_request


# COURSE
def query_list_courses(skip: int = 0, limit: int = 100) -> list:
    try:
        courses_cursor = db_client.course_coll.find(skip=skip, limit=limit)
        courses = []
        for course in courses_cursor:
            course["course_id"] = str(course["_id"])
            courses.append(course)
        return courses
    except InvalidId:
        raise Exception.bad_request


def create_course(course_body: PostCourseRequestModel) -> InsertOneResult:
    try:
        # Check valid teacher
        teacher_filter = {"type": teacher_type, "_id": ObjectId(course_body.teacher_id)}
        teacher_result = db_client.user_coll.find_one(filter=teacher_filter)
        if teacher_result == None:
            raise Exception.unprocessable_content

        # Check valid tag
        for tag_id in course_body.tag_ids:
            tag_result = db_client.tag_coll.find_one(ObjectId(tag_id))
            if tag_result == None:
                raise Exception.unprocessable_content

        body = {
            "name": course_body.name,
            "teacher_id": ObjectId(course_body.teacher_id),
            "description": course_body.description,
            "created_date": datetime.now(),
            "course_pic": str(course_body.course_pic),
            "student_count": 0,
            "rating": 0,
            "review_count": 0,
            "price": course_body.price,
            "course_objective": course_body.course_objective,
            "course_requirement": course_body.course_requirement,
            "difficulty_level": course_body.difficulty_level,
            "tags": list(map(ObjectId, course_body.tag_ids)),
            "total_video_length": 0,
            "chapter_count": 0,
            "file_count": 0,
            "quiz_count": 0,
            "video_count": 0,
            "status": "started",  # TODO: add not deployed status
        }

        result = db_client.course_coll.insert_one(document=body)
        return result

    except InvalidId:
        raise Exception.bad_request


# CHAPTER
def query_list_course_chapters(course_id: str, skip: int = 0, limit: int = 100) -> list:
    try:
        chapters_cursor = db_client.chapter_coll.find(
            {"course_id": ObjectId(course_id)}, skip=skip, limit=limit
        )
        chapters = []
        for chapter in chapters_cursor:
            chapter["chapter_id"] = str(chapter["_id"])
            chapters.append(chapter)
        return chapters
    except InvalidId:
        raise Exception.bad_request


def create_course_chapter(course_id: str, chapter_body: PostCourseChapterRequestModel):
    try:
        chapter_body_to_inserted = chapter_body.model_dump()
        chapter_body_to_inserted["course_id"] = ObjectId(course_id)
        chapter_body_to_inserted["description"] = chapter_body.description
        chapter_body_to_inserted["chapter_length"] = 0
        chapter_body_to_inserted["lesson_count"] = 0  # TODO: Check if need to change

        # No matching course
        valid_course_id_filter = {"_id": ObjectId(course_id)}
        result = db_client.course_coll.find_one(filter=valid_course_id_filter)
        if result == None:
            raise Exception.unprocessable_content

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
    except InvalidId:
        raise Exception.bad_request


def query_course_chapter(chapter_id: str):
    try:
        queried_chapter = db_client.chapter_coll.find_one({"_id": ObjectId(chapter_id)})
        if queried_chapter != None:
            queried_chapter["chapter_id"] = str(queried_chapter["_id"])
            queried_chapter["course_id"] = str(queried_chapter["course_id"])
        return queried_chapter
    except InvalidId:
        raise Exception.bad_request


def edit_course_chapter(
    chapter_id: str, chapter_to_edit: PatchCourseChapterRequestModel
):
    try:
        # print(chapter_to_edit)
        filter_chapter = {"_id": ObjectId(chapter_id)}
        chapter_to_edit_2 = {"$set": chapter_to_edit.model_dump(exclude_unset=True)}
        response = db_client.chapter_coll.update_one(filter_chapter, chapter_to_edit_2)
        if response.matched_count == 0:
            raise Exception.not_found
        return response
    except InvalidId:
        raise Exception.bad_request


def delete_course_chapter(chapter_id: str, course_id: str):
    try:
        chapter_delete_filter = {"_id": ObjectId(chapter_id)}
        delete_response = db_client.chapter_coll.find_one_and_delete(
            filter=chapter_delete_filter, projection={"chapter_num": True}
        )
        if delete_response == None:  # Deletion Failed.
            raise Exception.not_found
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
        return
    except InvalidId:
        raise Exception.bad_request


# LESSON
def query_list_course_lessons(
    course_id: str, chapter_id: str, skip: int = 0, limit: int = 100
) -> list:
    try:
        filter = {"course_id": ObjectId(course_id), "chapter_id": ObjectId(chapter_id)}
        lessons_cursor = db_client.lesson_coll.find(
            filter=filter, skip=skip, limit=limit
        )
        lessons = []
        for lesson in lessons_cursor:
            lesson["lesson_id"] = str(lesson["_id"])
            lessons.append(lesson)
        return lessons
    except InvalidId:
        raise Exception.bad_request


def query_course_lesson(course_id: str, chapter_id: str, lesson_id: str) -> dict | None:
    try:
        filter = {
            "_id": ObjectId(lesson_id),
            "course_id": ObjectId(course_id),
            "chapter_id": ObjectId(chapter_id),
        }
        lesson = db_client.lesson_coll.find_one(filter=filter)
        if lesson != None:
            lesson["lesson_id"] = str(lesson["_id"])
        return lesson
    except InvalidId:
        raise Exception.bad_request


def create_course_lesson(
    course_id: str, chapter_id: str, request: PostCourseLessonRequestModel
) -> str:
    try:
        # Check for valid course and chapter
        valid_course_filter = {"_id": ObjectId(course_id)}
        course_result = db_client.course_coll.find_one(filter=valid_course_filter)
        if course_result == None:
            raise Exception.unprocessable_content
        valid_chapter_filter = {"_id": ObjectId(chapter_id)}
        chapter_result = db_client.chapter_coll.find_one(filter=valid_chapter_filter)
        if chapter_result == None:
            raise Exception.unprocessable_content

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
    except InvalidId:
        raise Exception.bad_request


def edit_course_lesson(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
    request: PatchCourseLessonRequestModel,
) -> UpdateResult:
    try:
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
        if result.matched_count == 0:
            raise Exception.not_found
        return result
    except InvalidId:
        raise Exception.bad_request


def remove_course_lesson(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
):
    try:
        delete_filter = {
            "_id": ObjectId(lesson_id),
            "course_id": ObjectId(course_id),
            "chapter_id": ObjectId(chapter_id),
        }
        result = db_client.lesson_coll.find_one_and_delete(delete_filter)
        if result == None:  # Deletion Failed.
            raise Exception.not_found
        lesson_num_threshold = result["lesson_num"]

        update_filter = {
            "course_id": ObjectId(course_id),
            "chapter_id": ObjectId(chapter_id),
            "lesson_num": {"$gt": lesson_num_threshold},
        }

        update_body = {"$inc": {"lesson_num": -1}}
        result = db_client.lesson_coll.update_many(
            filter=update_filter, update=update_body
        )
        return

    except InvalidId:
        raise Exception.bad_request
