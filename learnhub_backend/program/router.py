from fastapi import APIRouter, Depends
from typing import Annotated
from pydantic import TypeAdapter

from ..dependencies import common_pagination_parameters
from .schemas import Programs_model,Program_model
from .database import query_list_programs


router = APIRouter(
        prefix="/programs",
        tags=['program'],
        dependencies=[Depends(common_pagination_parameters)]
        )

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]

@router.get("/", status_code=200, response_model_exclude_none=True)
def list_programs(common_paginations: common_page_params) -> Programs_model:
        queried_programs = query_list_programs(common_paginations["skip"], common_paginations["limit"])
        ta = TypeAdapter(list[Program_model])
        response_body = Programs_model(programs=ta.validate_python(queried_programs))
        return  response_body
