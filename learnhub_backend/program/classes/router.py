from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ...dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    list_classes_response,
    get_class_response,
)

from .schemas import (
    ListClassesResponseModel,
    GetClassResponseModel,
)

router = APIRouter(
    prefix="/programs/classes",
    tags=["classes"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


# CLASSES
@router.get(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListClassesResponseModel,
)
def list_classes(common_paginations: common_page_params):
    response_body = list_classes_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


@router.get(
    "/{class_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetClassResponseModel,
)
def get_class(class_id: str):
    response_body = get_class_response(class_id=class_id)
    return response_body
