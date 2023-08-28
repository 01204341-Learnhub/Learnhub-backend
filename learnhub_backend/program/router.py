from fastapi import APIRouter, Depends
from typing import Annotated
from pydantic import TypeAdapter

from ..dependencies import common_pagination_parameters
from learnhub_backend.program.schemas import Programs,Program


router = APIRouter(
        prefix="/programs",
        tags=['program'],
        dependencies=[Depends(common_pagination_parameters)]
        )

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency) ]

@router.get("/", status_code=200)
def list_programs(common_paginations: common_page_params) -> Programs:
        mock_data = {
                        "programs":[
                            {
                            "course_id": "1234",
                            "type":"course",
                            "name":"Discreet Math"
                                }
                            ]
                        }
        ta = TypeAdapter(list[Program])
        response_body = Programs(programs=ta.validate_python(mock_data["programs"]))
        return  response_body
