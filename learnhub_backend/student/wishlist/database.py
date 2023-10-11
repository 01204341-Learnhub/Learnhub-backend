from logging import error
from pymongo.cursor import Cursor
from pymongo.results import DeleteResult, UpdateResult
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from bson.errors import InvalidId

from .schemas import place_holder_model
from ..database import db_client


from learnhub_backend.dependencies import (
    student_type,
    teacher_type,
    course_type,
    class_type,
    Exception,
)


def place_holder_db():
    pass


def query_class_or_course(program_id: str, program_type: str) -> Cursor:
    try:
        filter_ = {"_id": ObjectId(program_id)}
        projection = {"_id": 1, "name": 1, "price": 1}
        if program_type == course_type:
            program = db_client.course_coll.find_one(
                filter=filter_, projection=projection
            )
        elif program_type == class_type:
            program = db_client.class_coll.find_one(
                filter=filter_, projection=projection
            )
        else:
            raise Exception.bad_request
        return program
    except InvalidId:
        raise Exception.bad_request


# WISSLIST
def query_wishlist(student_id: str) -> list:
    try:
        filter_ = {"_id": ObjectId(student_id), "type": student_type}
        user = db_client.user_coll.find_one(filter=filter_)
        if user is None:
            raise Exception.not_found
        return user["wishlist"]
    except InvalidId:
        raise Exception.bad_request
