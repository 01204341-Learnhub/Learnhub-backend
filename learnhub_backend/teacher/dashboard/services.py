from datetime import datetime, timezone, tzinfo
from typing import Annotated, Union
from bson.objectid import ObjectId
from pydantic import HttpUrl, TypeAdapter
from pymongo.results import DeleteResult, UpdateResult

from learnhub_backend.dependencies import (
    GenericOKResponse,
    Exception,
    class_type,
    course_type,
    student_type,
    teacher_type,
    get_timestamp_from_datetime,
)

from .config import (
    _Program,
)
