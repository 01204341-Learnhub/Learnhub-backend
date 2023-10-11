from pydantic import TypeAdapter


from learnhub_backend.dependencies import GenericOKResponse

from .database import (
    purchase,
)

from .schemas import (
    PostPurchaseRequestModel,
    PostPurchaseResponseModel,
)


def post_purchase(
    request: PostPurchaseRequestModel,
) -> PostPurchaseResponseModel:
    transaction_id = purchase(request)
    return PostPurchaseResponseModel(transaction_id=transaction_id)
