from pydantic import TypeAdapter
from datetime import datetime
from learnhub_backend.dependencies import GenericOKResponse, Exception
from .database import (
    place_holder_db_service
)
from .schemas import (
    PlaceHolderModel
)

def place_holder_service():
    pass

def get_quiz_response(quiz_id : str):
    response_body = query_quiz(
        quiz_id=quiz_id ,
    )
    return response_body


