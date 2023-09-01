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
    chapter_id = db_client.chapter_coll.insert_one(chapter_body_to_inserted).inserted_id

    return {"chapter_id": str(chapter_id)}


def query_find_course_chapter(chapter_id: str):
    queried_chapter = db_client.chapter_coll.find_one({"_id": ObjectId(chapter_id)})
    queried_chapter["chapter_id"] = str(queried_chapter["_id"])
    return queried_chapter


def query_edit_course_chapter(
    chapter_id: str, chapter_to_edit: EditCourseChapterRequestModel
):
    # print(chapter_to_edit)
    filter_chapter = {"_id": ObjectId(chapter_id)}
    chapter_to_edit_2 = {"$set": chapter_to_edit.model_dump(exclude_unset=True)}
    resposne = db_client.chapter_coll.update_one(filter_chapter, chapter_to_edit_2)
    return resposne

def query_delete_course_chapter(chapter_id: str):
    filter_chapter = {"_id": ObjectId(chapter_id)}
    resposne = db_client.chapter_coll.delete_one(filter_chapter)
    return resposne

    # db_client.chapter_coll.update_one()


# pprint.pprint(query_list_course_chapters(course_id="64eaf639565900315d349e49"))
