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

def place_holder_db_service():
    pass