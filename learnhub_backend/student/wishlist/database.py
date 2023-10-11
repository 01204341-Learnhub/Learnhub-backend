from logging import error
from pymongo.cursor import Cursor
from pymongo.results import DeleteResult, UpdateResult
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from bson.errors import InvalidId

from .schemas import (
    place_holder_model
)
from ..database import db_client


from learnhub_backend.dependencies import (
    student_type,
    teacher_type,
    course_type,
    Exception,
)

def place_holder_db():
    pass
