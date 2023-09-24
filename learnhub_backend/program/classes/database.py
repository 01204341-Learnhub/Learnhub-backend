from pymongo.results import UpdateResult
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId
from .schemas import (
    placeholder
)

from ...dependencies import Exception

def db_placeholder():
    return 0