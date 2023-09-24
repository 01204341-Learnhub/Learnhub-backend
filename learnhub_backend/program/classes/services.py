from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import UpdateResult

from learnhub_backend.dependencies import GenericOKResponse

from .database import (
    db_placeholder
)
from .schemas import (
    placeholder
)

from ...dependencies import Exception

def service_placeholder():
    return 0