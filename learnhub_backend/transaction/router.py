from fastapi import APIRouter, Depends
from typing import Annotated, Union

from learnhub_backend.transaction.schemas import (
    PostCoursePurchaseRequestModel,
    PostCoursePurchaseResponseModel,
)
from .services import (
    post_purchase_course,
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
    "/course/purchase",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostCoursePurchaseResponseModel,
)
def PostCoursePurchase(request_body: PostCoursePurchaseRequestModel):
    response_body = post_purchase_course(request_body)
    return response_body
