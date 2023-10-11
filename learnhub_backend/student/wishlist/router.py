from fastapi import APIRouter, Depends
from typing import Annotated

from learnhub_backend.dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    place_holder_service
)

from .schemas import (
    place_holder_model,
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
    response_model=dict,
)
def list_students(student_id:str ,common_paginations: common_page_params):
    return {"id": student_id}
    response_body = list_students_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


