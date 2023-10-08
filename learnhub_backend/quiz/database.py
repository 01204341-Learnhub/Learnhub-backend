from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId
import pprint

from .schemas import (
    PatchQuizResultRequestModel,
    GetQuizResponseModel,
    GetQuizResultResponseModel,
    PostQuizRequestModel,
)
from learnhub_backend.database import db_client
from learnhub_backend.dependencies import (
    Exception,
)


# QUIZ
def query_quiz(
    quiz_id: str,
):
    try:
        filter = {"_id": ObjectId(quiz_id)}
        quiz = db_client.quiz_coll.find_one(filter=filter)
        if quiz is None:
            raise Exception.not_found
        return quiz
    except InvalidId:
        raise Exception.bad_request


def query_quiz_result(
    quiz_id: str,
    student_id: str,
):
    try:
        filter = {"quiz_id": ObjectId(quiz_id), "student_id": ObjectId(student_id)}
        quiz = db_client.quiz_result_coll.find_one(filter=filter)
        if quiz is None:
            raise Exception.not_found
        return quiz
    except InvalidId:
        raise Exception.bad_request


def create_quiz(request: PostQuizRequestModel) -> str:
    quiz_problems = []
    for problem in request.problems:
        quiz_problems.append(
            {
                "problem_num": problem.problem_num,
                "question": problem.question,
                "multiple_correct_answers": problem.multiple_correct_answers,
                "explanation": problem.explanation,
                "choice": problem.choice.model_dump(),
                "correct_answer": problem.correct_answer.model_dump(),
            }
        )
    quiz_body = {
        "name": request.name,
        "description": request.description,
        "time_limit": request.time_limit,
        "quiz_pic": str(request.quiz_pic),
        "problems": quiz_problems,
    }

    result = db_client.quiz_coll.insert_one(quiz_body)
    if result == None:
        raise Exception.internal_server_error
    return str(result.inserted_id)


def edit_quiz_result(quiz_id: str, student_id: str, score_inc: int, answers_body: dict):
    try:
        filter = {"quiz_id": ObjectId(quiz_id), "student_id": ObjectId(student_id)}
        # prepare update body
        update_body_edit = {
            "$set": {},
            "$inc": {"score": score_inc},
        }
        array_filter = []

        # set update body for each field
        if answers_body["status"] is not None:
            update_body_edit["$set"]["status"] = answers_body["status"]
        if answers_body["answers"] is not None:
            for i in range(len(answers_body["answers"])):
                # set array filter and update body for each
                array_filter.append(
                    # filter to find document to update in array
                    {f"elem{i}.problem_num": answers_body["answers"][i]["problem_num"]}
                )

                # update body for document to update in array
                update_body_edit["$set"][f"problems.$[elem{i}].answer"] = answers_body[
                    "answers"
                ][i]["answer"]

                update_body_edit["$set"][
                    f"problems.$[elem{i}].is_correct"
                ] = answers_body["answers"][i]["is_correct"]

        # pprint.pprint(update_body_edit)
        # pprint.pprint(array_filter)
        result = db_client.quiz_result_coll.update_one(
            filter=filter, update=update_body_edit, array_filters=array_filter
        )
        if result.matched_count == 0:
            raise Exception.not_found
        return True

    except InvalidId:
        raise Exception.bad_request
