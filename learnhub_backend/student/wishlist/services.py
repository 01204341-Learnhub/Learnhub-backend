from bson.objectid import ObjectId
from pydantic import TypeAdapter
from learnhub_backend.dependencies import (
    GenericOKResponse,
    Exception,
    mongo_datetime_to_timestamp,
)
from .database import query_wishlist, query_class_or_course
from .schemas import (
    GetWishListResponseModel,
)


def place_holder_service():
    pass


# WISSLIST
def get_wishlist_response(
    student_id: str,
):
    wishlist = query_wishlist(student_id=student_id)
    for item in wishlist:
        item["wishlist_item_id"] = str(item["wishlist_item_id"])
        item["program_id"] = str(item["program_id"])
        program = query_class_or_course(
            program_id=item["program_id"], program_type=item["type"]
        )
        item["name"] = program["name"]
        item["price"] = program["price"]

    return GetWishListResponseModel(wishlist=wishlist)
