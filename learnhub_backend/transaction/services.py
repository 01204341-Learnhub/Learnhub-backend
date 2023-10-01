from typing import Annotated, Union
from bson.objectid import ObjectId
from pydantic import TypeAdapter
from pymongo.results import DeleteResult, UpdateResult

from learnhub_backend.dependencies import GenericOKResponse

from .database import (
    purchase_course,
)

from .schemas import (
    PostCoursePurchaseRequestModel,
    PostCoursePurchaseResponseModel,
)


def post_purchase_course(
    request: PostCoursePurchaseRequestModel,
) -> PostCoursePurchaseResponseModel:
    transaction_id = purchase_course(request)
    return PostCoursePurchaseResponseModel(transaction_id=transaction_id)
