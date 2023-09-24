from pymongo.results import UpdateResult
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId
from .schemas import (
    placeholder,
    placeholder,
)

from ...dependencies import Exception


def db_placeholder():
    return 0


# CLASSES
def query_list_classes(skip: int, limit: int):# TODO: add return type
    try:
        classes_corsor = db_client.class_coll.find(skip=skip, limit=limit)
    except InvalidId:
        raise Exception.bad_request
    return classes_corsor
