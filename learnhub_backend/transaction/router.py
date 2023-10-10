from fastapi import APIRouter, Depends
from typing import Annotated, Union

from learnhub_backend.transaction.schemas import (
    PostPurchaseRequestModel,
    PostPurchaseResponseModel,
)
from .services import (
    post_purchase,
)


from ..dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

router = APIRouter(
    prefix="/transactions",
    tags=["transaction"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


@router.post(
    "/purchase",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostPurchaseResponseModel,
)
def PostPurchase(request_body: PostPurchaseRequestModel):
    response_body = post_purchase(request_body)
    return response_body
