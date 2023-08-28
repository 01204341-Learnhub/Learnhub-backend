from ..database import db_client
from .config import db_course_collection, db_chapter_collection,db_lesson_collection

def query_list_programs(skip: int = 0, limit: int = 100) -> list:
    courses_cursor = db_client[db_course_collection].find(skip=skip, limit=limit)
    programs = []
    for course in courses_cursor:
        course["course_id"] = str(course["_id"])
        course["type"] = "program"
        programs.append(course)
    return programs


