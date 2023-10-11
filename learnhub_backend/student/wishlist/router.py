from fastapi import APIRouter, Depends
from typing import Annotated

from learnhub_backend.dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import place_holder_service,get_wishlist_response

from .schemas import (
    place_holder_model,
    GetWishListResponseModel,
)


router = APIRouter(
    prefix="/users/students/{student_id}/wishlist",
    tags=["wishlist"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


@router.get(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetWishListResponseModel,
)
def get_wishlist(
    student_id: str,
):
    response_body = get_wishlist_response(
        student_id=student_id,
    )
    return response_body
