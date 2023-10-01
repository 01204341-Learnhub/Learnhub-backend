from pydantic import TypeAdapter
from datetime import datetime
from learnhub_backend.dependencies import GenericOKResponse, Exception
from .database import query_quiz
from .schemas import GetQuizResponseModel


def place_holder_service():
    pass


def get_quiz_response(quiz_id: str):
    queried_quiz = query_quiz(
        quiz_id=quiz_id,
    )
    return GetQuizResponseModel(**queried_quiz)
