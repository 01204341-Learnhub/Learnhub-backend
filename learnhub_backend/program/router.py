from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ..dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .schemas import (
    ListProgramsResponseModel,
    ListTagsResponseModel,
)

from .services import (
    list_programs_response,
    list_tags_response,
)


router = APIRouter(
    prefix="/programs",
    tags=["program"],
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
    response_model=ListProgramsResponseModel,
    response_model_exclude_none=True,
)
def list_programs(common_paginations: common_page_params):
    response_body = list_programs_response(
        common_paginations["skip"], common_paginations["limit"]
    )
    return response_body


@router.get(
    "/tags",
    status_code=200,
    response_model=ListTagsResponseModel,
    response_model_exclude_none=True,
)
def list_tags(common_paginations: common_page_params):
    response_body = list_tags_response(
        common_paginations["skip"], common_paginations["limit"]
    )
    return response_body
