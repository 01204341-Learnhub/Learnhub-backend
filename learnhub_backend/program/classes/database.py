from pymongo.results import UpdateResult
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId
from .schemas import (
    TagModelBody,

)

from ...dependencies import Exception

#TODO: optional add this to dependencies
def get_teacher_by_id(teacher_id: str):
    try:
        teacher = db_client.user_coll.find_one({"_id": ObjectId(teacher_id)})
        if teacher is None:
            raise Exception.not_found
        teacher["teacher_id"] = str(teacher["_id"])
        teacher["teacher_name"] = teacher["fullname"]
        return teacher
    except InvalidId:
        raise Exception.bad_request

def query_list_tags_by_id(ids: list[str | ObjectId]):
    try:
        object_ids = list(map(ObjectId, ids))

        filter = {"_id": {"$in": object_ids}}
        tags_cursor = db_client.tag_coll.find(filter)
        tags = []
        for tag in tags_cursor:
            tag["tag_id"] = str(tag["_id"])
            tag["tag_name"] = tag["name"]
            tags.append(TagModelBody(**tag))
        return tags

    except InvalidId:
        raise Exception.bad_request

# CLASSES
def query_list_classes(skip: int, limit: int):# TODO: add return type
    try:
        classes_corsor = db_client.class_coll.find(skip=skip, limit=limit)
    except InvalidId:
        raise Exception.bad_request
    return classes_corsor
