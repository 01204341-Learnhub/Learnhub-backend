from datetime import datetime, timedelta, timezone
from pymongo.results import DeleteResult, UpdateResult
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ..database import db_client

from ..dependencies import (
    student_type,
    course_type,
    class_type,
    Exception,
)

from .schemas import (
    PostPurchaseRequestModel,
)


class _program:
    def __init__(self, program_id: str, type: str):
        self.program_id = program_id
        self.type = type


# PURCHASE
def purchase(request: PostPurchaseRequestModel) -> str:
    transaction_id = ""
    programs: list[_program] = []

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
        if basket_item["type"] == "course":
            # get course
            course_filter = {"_id": ObjectId(basket_item["program_id"])}
            course = db_client.course_coll.find_one(course_filter)
            if course == None:
                e = Exception.not_found
                e.__setattr__("detail", "Course not found")
                raise e
            update_purchase_list = {
                "type": "course",
                "price": course["price"],
                "program_id": ObjectId(basket_item["program_id"]),
            }
            total_price += course["price"]
        elif basket_item["type"] == "class":
            # get class
            class_filter = {"_id": ObjectId(basket_item["program_id"])}
            class_ = db_client.class_coll.find_one(class_filter)
            if class_ == None:
                e = Exception.not_found
                e.__setattr__("detail", "Class not found")
                raise e

            if class_["registration_ended_date"] > datetime.now(
                tz=timezone(timedelta(hours=7))
            ):
                e = Exception.unprocessable_content
                e.__setattr__("detail", "Registration period has ended")
                raise e

            update_purchase_list = {
                "type": "class",
                "price": class_["price"],
                "program_id": ObjectId(basket_item["program_id"]),
            }
            total_price += class_["price"]
        else:
            raise Exception.unprocessable_content

        programs.append(_program(basket_item["program_id"], basket_item["type"]))
        transaction_body["purchase_list"].append(update_purchase_list)

    # create transaction
    transaction_body["total_price"] = total_price
    transaction_add_result = db_client.transaction_coll.insert_one(transaction_body)
    if transaction_add_result.inserted_id == None:
        raise Exception.internal_server_error
    transaction_id = str(transaction_add_result.inserted_id)

    # update own programs
    _update_own_program_on_purchase(str(request.student_id), programs)

    # create student's course progress
    _update_course_progress_on_purchase(str(request.student_id), programs)

    _update_assignment_submission_on_purchase(str(request.student_id), programs)

    # update course's and class's fields
    _update_programs_on_purchase(programs)

    # remove student's basket items
    _update_basket_on_purchase_complete(str(request.student_id))
    return transaction_id


def _update_basket_on_purchase_complete(student_id: str):
    filter = {"_id": ObjectId(student_id), "type": student_type}
    update = {"$set": {"basket": []}}
    result = db_client.user_coll.update_one(filter, update)
    if result.matched_count == 0:
        raise Exception.internal_server_error


def _update_own_program_on_purchase(student_id: str, programs: list[_program]):
    filter = {"type": student_type, "_id": ObjectId(student_id)}
    own_programs = []
    for prog_ in programs:
        own_programs.append({"type": prog_.type, "program_id": prog_.program_id})

    update = {"$push": {"owned_programs": {"$each": own_programs}}}

    result = db_client.user_coll.update_one(filter, update)
    if result.matched_count == 0:
        raise Exception.internal_server_error


def _update_assignment_submission_on_purchase(
    student_id: str, programs: list[_program]
):
    submissions = []
    for prog_ in programs:
        if prog_.type == class_type:
            assignment_filter = {"class_id": ObjectId(prog_.program_id)}
            assignments_cur = db_client.assignment_coll.find(assignment_filter)
            for assignment_ in assignments_cur:
                submissions.append(
                    {
                        "class_id": ObjectId(prog_.program_id),
                        "assignment_id": assignment_["_id"],
                        "status": "unsubmit",
                        "score": 0,
                        "submission_date": datetime.fromtimestamp(0),
                        "attachments": [],
                        "student_id": ObjectId(student_id),
                    }
                )
    if len(submissions) == 0:
        return
    result = db_client.assignment_submission_coll.insert_many(submissions)
    if len(result.inserted_ids) == 0:
        raise Exception.internal_server_error


def _update_course_progress_on_purchase(student_id: str, programs: list[_program]):
    progresses = []
    for _program in programs:
        if _program.type == course_type:
            progress = dict()
            progress["student_id"] = ObjectId(student_id)
            progress["course_id"] = _program.program_id
            progress["finished"] = False
            progress["finished_count"] = 0
            progress["lessons"] = []

            lessons_filter = {"course_id": ObjectId(_program.program_id)}
            lessons_cur = db_client.lesson_coll.find(lessons_filter)
            for lesson in lessons_cur:
                if lesson["lesson_type"] == "quiz":
                    _create_student_quiz_result(student_id, str(lesson["src"]))
                progress["lessons"].append(
                    {
                        "lesson_id": lesson["_id"],
                        "chapter_id": lesson["chapter_id"],
                        "finished": False,
                        "lesson_completed": 0,
                    }
                )
            progresses.append(progress)

    if len(progresses) == 0:
        return
    _ = db_client.course_progress_coll.insert_many(progresses)


def _create_student_quiz_result(student_id: str, quiz_id: str):
    quiz_filter = {"_id": ObjectId(quiz_id)}
    quiz = db_client.quiz_coll.find_one(quiz_filter)
    if quiz == None:
        raise Exception.internal_server_error
    body = {
        "score": 0,
        "problems": [],
        "status": "not started",
        "quiz_id": ObjectId(quiz_id),
        "student_id": ObjectId(student_id),
    }
    for problem in quiz["problems"]:
        body["problems"].append(
            {
                "problem_num": problem["problem_num"],
                "is_correct": False,
                "answer": {
                    "answer_a": False,
                    "answer_b": False,
                    "answer_c": False,
                    "answer_d": False,
                    "answer_e": False,
                    "answer_f": False,
                },
            }
        )
    _ = db_client.quiz_result_coll.insert_one(body)


def _update_programs_on_purchase(programs: list[_program]):
    for prog_ in programs:
        filter = {"_id": prog_.program_id}
        update = {"$inc": {"student_count": 1}}
        if prog_.type == course_type:
            result = db_client.course_coll.update_one(filter, update)
        elif prog_.type == class_type:
            result = db_client.class_coll.update_one(filter, update)
        else:
            raise Exception.unprocessable_content
        if result.matched_count == 0:
            raise Exception.internal_server_error
