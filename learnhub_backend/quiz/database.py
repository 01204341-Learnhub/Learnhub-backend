from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId
import pprint

from .schemas import (
    PlaceHolderModel,
)
from learnhub_backend.database import db_client
from learnhub_backend.dependencies import (
    Exception,
    CheckHttpFileType,
)


def query_quiz(
    quiz_id: str,
) -> dict:
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
) -> dict:
    try:
        filter = {"quiz_id": ObjectId(quiz_id), "student_id": ObjectId(student_id)}
        quiz = db_client.quiz_result_coll.find_one(filter=filter)
        if quiz is None:
            raise Exception.not_found
        return quiz
    except InvalidId:
        raise Exception.bad_request

