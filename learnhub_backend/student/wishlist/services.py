from bson.objectid import ObjectId
from pydantic import TypeAdapter
from learnhub_backend.dependencies import GenericOKResponse,Exception, mongo_datetime_to_timestamp
from .database import (
    place_holder_db
)
from .schemas import (
    place_holder_model,
)

def place_holder_service():
    pass


