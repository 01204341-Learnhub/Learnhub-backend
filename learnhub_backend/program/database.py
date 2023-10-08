from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo.cursor import Cursor

from ..database import (
    db_client,
)

from ..dependencies import Exception


def query_list_programs(skip: int = 0, limit: int = 100) -> list:
    try:
        courses_cursor = db_client.course_coll.find(skip=skip, limit=limit)
        programs = []
        for course in courses_cursor:
            course["course_id"] = str(course["_id"])
            course["type"] = "program"
            programs.append(course)
        # TODO: add class query

        return programs
    except InvalidId:
        raise Exception.bad_request


# TAGS
def query_list_tags(skip: int = 0, limit: int = 100) -> Cursor:
    try:
        tags_cur = db_client.tag_coll.find(skip=skip, limit=limit)
        return tags_cur
    except InvalidId:
        raise Exception.bad_request
