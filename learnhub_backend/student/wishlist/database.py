from logging import error
from pymongo.cursor import Cursor
from pymongo.results import DeleteResult, UpdateResult
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from bson.errors import InvalidId

from .schemas import PostWishListItemRequestModel
from ..database import db_client


from learnhub_backend.dependencies import (
    student_type,
    teacher_type,
    course_type,
    class_type,
    Exception,
)


# WISSLIST
def query_class_or_course(program_id: str, program_type: str) -> dict:
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
            err = Exception.unprocessable_content
            err.__setattr__("detail", "Invalid program type")
            raise err
        if program is None:
            raise Exception.not_found
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


def add_wishlist_item(
    student_id: str, wishlist_item_body: PostWishListItemRequestModel
):
    try:
        # check if program exists
        query_class_or_course(
            program_id=wishlist_item_body.program_id,
            program_type=wishlist_item_body.type,
        )

        # check if item already exists in wishlist
        wishlist = query_wishlist(student_id=student_id)
        for item in wishlist:
            if item["program_id"] == wishlist_item_body.program_id:
                err = Exception.bad_request
                err.__setattr__("detail", "Item already exists in wishlist")
                raise err

        # add item to wishlist
        filter_ = {"_id": ObjectId(student_id), "type": student_type}
        push_body = {"wishlist": wishlist_item_body.model_dump()}
        push_body["wishlist"]["wishlist_item_id"] = ObjectId()
        update_result = db_client.user_coll.update_one(
            filter=filter_, update={"$push": push_body}
        )
        if update_result.matched_count == 0:
            raise Exception.not_found
    except InvalidId:
        raise Exception.bad_request


def remove_wishlist_item(student_id: str, wishlist_item_id: str):
    try:
        filter_ = {"_id": ObjectId(student_id), "type": student_type}
        pull_content = {}
        pull_content["wishlist"] = {"wishlist_item_id": ObjectId(wishlist_item_id)}
        update_result = db_client.user_coll.update_one(
            filter=filter_, update={"$pull": pull_content}
        )
        if update_result.matched_count == 0:
            raise Exception.not_found
        return True
    except InvalidId:
        raise Exception.bad_request
