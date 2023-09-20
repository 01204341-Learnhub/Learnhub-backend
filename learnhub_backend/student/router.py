from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ..dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    list_students_response,
)

from .schemas import (
    ListStudentsResponseModel,
)


router = APIRouter(
    prefix="/users/students",
    tags=["student"],
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
    response_model=ListStudentsResponseModel,
)
def list_students(common_paginations: common_page_params):
    response_body = list_students_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


@router.get(
    "/{student_id}",
    status_code=200,
)
def get_student(student_id: str, common_paginations: common_page_params):
    pass
