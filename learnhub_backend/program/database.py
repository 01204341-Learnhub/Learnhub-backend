from ..database import db_client
from bson.objectid import ObjectId
from .schemas import AddCourseChaptersRequestModel, EditCourseChapterRequestModel
import pprint


def query_list_programs(skip: int = 0, limit: int = 100) -> list:
    courses_cursor = db_client.course_coll.find(skip=skip, limit=limit)
    programs = []
    for course in courses_cursor:
        course["course_id"] = str(course["_id"])
        course["type"] = "program"
        programs.append(course)
    # TODO: add class query

    return programs


def query_list_course_chapters(course_id: str, skip: int = 0, limit: int = 100) -> list:
    chapters_cursor = db_client.chapter_coll.find({"course_id": ObjectId(course_id)})
    chapters = []
    for chapter in chapters_cursor:
        chapter["chapter_id"] = str(chapter["_id"])
        chapters.append(chapter)
    return chapters


def query_add_course_chapter(
    course_id: str, chapter_body: AddCourseChaptersRequestModel
):
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


def query_find_course_chapter(chapter_id: str):
    queried_chapter = db_client.chapter_coll.find_one({"_id": ObjectId(chapter_id)})
    if queried_chapter != None:
        queried_chapter["chapter_id"] = str(queried_chapter["_id"])
        queried_chapter["course_id"] = str(queried_chapter["course_id"])
    return queried_chapter


def query_edit_course_chapter(
    chapter_id: str, chapter_to_edit: EditCourseChapterRequestModel
):
    # print(chapter_to_edit)
    filter_chapter = {"_id": ObjectId(chapter_id)}
    chapter_to_edit_2 = {"$set": chapter_to_edit.model_dump(exclude_unset=True)}
    response = db_client.chapter_coll.update_one(filter_chapter, chapter_to_edit_2)
    return response


def query_delete_course_chapter(chapter_id: str, course_id: str) -> int:
    chapter_delete_filter = {"_id": ObjectId(chapter_id)}
    delete_response = db_client.chapter_coll.find_one_and_delete(filter=chapter_delete_filter,projection={"chapter_num":True})
    if delete_response == None:  # Deletion Failed.
        return 0
    chapter_num_threshold = delete_response["chapter_num"]
    chapter_update_filter = {
        "course_id": ObjectId(course_id),
        "chapter_num": {"$gt": chapter_num_threshold},
    }
    update_body = {"$inc": {"chapter_num": -1}}
    update_response = db_client.chapter_coll.update_many(filter=chapter_update_filter, update=update_body)
    return 1


    # db_client.chapter_coll.update_one()


# pprint.pprint(query_list_course_chapters(course_id="64eaf639565900315d349e49"))
