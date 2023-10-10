from datetime import datetime
from typing import Annotated, Union
from bson.objectid import ObjectId
from pydantic import TypeAdapter
from pymongo.results import DeleteResult, UpdateResult

from learnhub_backend.dependencies import GenericOKResponse
