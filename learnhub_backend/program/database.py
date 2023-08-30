from ..database import db_client
from bson.objectid import ObjectId
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

def query_list_course_chapters( course_id: str , skip: int = 0, limit: int = 100) -> list:
    courses_cursor = db_client.course_coll.find_one( {"_id": ObjectId(course_id)})
    list_chapters_id = courses_cursor["chapters"]
    chapters = []
    for chapter_id in list_chapters_id:
        chapter = db_client.chapter_coll.find_one({"_id": chapter_id})
        chapter["chapter_id"] = str(chapter["_id"])
        chapters.append(chapter)
    return chapters

#pprint.pprint(query_list_course_chapters(course_id="64eaf639565900315d349e49"))