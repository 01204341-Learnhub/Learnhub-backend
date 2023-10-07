from datetime import datetime
from pymongo.results import DeleteResult, UpdateResult
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..database import db_client

from ..dependencies import (
    student_type,
    course_type,
    Exception,
)

from .schemas import (
    PostCoursePurchaseRequestModel,
)


# COURSE PURCHASE
def purchase_course(request: PostCoursePurchaseRequestModel) -> str:
    transaction_id = ""
    course_ids: list[ObjectId] = []

    # get student

    student_filter = {"type": student_type, "_id": ObjectId(request.student_id)}
    student = db_client.user_coll.find_one(student_filter)
    if student == None:
        e = Exception.not_found
        e.__setattr__("detail", "Student not found")
        raise e
    basket = student["basket"]
    if len(basket) == 0:
        e = Exception.unprocessable_content
        e.__setattr__("detail", "Atleast one basket item required")
        raise e
    # TODO: Implement Payment updates on teacher and students

    total_price = 0
    transaction_body = dict()  # update transaction body
    transaction_body["user_id"] = ObjectId(request.student_id)
    transaction_body["purchase_time"] = datetime.now()
    transaction_body["purchase_list"] = []

    # for item in basket buy
    for _, basket_item in enumerate(basket):
        # get course
        course_filter = {"_id": ObjectId(basket_item["program_id"])}
        course = db_client.course_coll.find_one(course_filter)

        course_ids.append(basket_item["program_id"])
        if course == None:
            e = Exception.not_found
            e.__setattr__("detail", "Course not found")
            raise e
        update_purchase_list = {
            "type": "course",
            "price": course["price"],
            "program_id": ObjectId(basket_item["program_id"]),
        }
        transaction_body["purchase_list"].append(update_purchase_list)
        total_price += course["price"]

    # create transaction
    transaction_body["total_price"] = total_price
    transaction_add_result = db_client.transaction_coll.insert_one(transaction_body)
    if transaction_add_result.inserted_id == None:
        raise Exception.internal_server_error
    transaction_id = str(transaction_add_result.inserted_id)

    # update own courses
    _update_own_course_on_purchase(str(request.student_id), course_ids)

    # create student's course progress
    _update_course_progress_on_purchase(str(request.student_id), course_ids)

    # update course's fields
    _update_course_on_purchase(course_ids)

    # remove student's basket items
    _update_basket_on_purchase_complete(str(request.student_id))
    return transaction_id


def _update_basket_on_purchase_complete(student_id: str):
    filter = {"_id": ObjectId(student_id), "type": student_type}
    update = {"$set": {"basket": []}}
    result = db_client.user_coll.update_one(filter, update)
    if result.matched_count == 0:
        raise Exception.internal_server_error


def _update_own_course_on_purchase(student_id: str, course_ids: list[ObjectId]):
    filter = {"type": student_type, "_id": ObjectId(student_id)}
    own_course = []
    for course_id in course_ids:
        own_course.append({"type": course_type, "program_id": course_id})

    update = {"$push": {"owned_programs": {"$each": own_course}}}

    result = db_client.user_coll.update_one(filter, update)
    if result.matched_count == 0:
        raise Exception.internal_server_error


def _update_course_progress_on_purchase(student_id: str, course_ids: list[ObjectId]):
    progresses = []
    for course_id in course_ids:
        progress = dict()
        progress["student_id"] = ObjectId(student_id)
        progress["course_id"] = course_id
        progress["finished"] = False
        progress["finished_count"] = 0
        progress["lessons"] = []

        lessons_filter = {"course_id": ObjectId(course_id)}
        lessons_cur = db_client.lesson_coll.find(lessons_filter)
        for lesson in lessons_cur:
            # TODO: check if lesson_type is quiz then make quiz_result for this student
            progress["lessons"].append(
                {
                    "lesson_id": lesson["_id"],
                    "chapter_id": lesson["chapter_id"],
                    "finished": False,
                    "lesson_completed": 0,
                }
            )
        progresses.append(progress)

    _ = db_client.course_progress_coll.insert_many(progresses)


def _update_course_on_purchase(course_ids: list[ObjectId]):
    for course_id in course_ids:
        filter = {"_id": course_id}
        update = {"$inc": {"student_count": 1}}
        result = db_client.course_coll.update_one(filter, update)
        if result.matched_count == 0:
            raise Exception.internal_server_error
