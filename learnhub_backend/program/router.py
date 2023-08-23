from fastapi import APIRouter, Depends
from typing import Annotated

from dependencies import common_pagination_parameters


router = APIRouter(
        prefix="/programs",
        tags=['program'],
        )

@router.get("/", status_code=200)
async def list_programs(common_paginations: Annotated[dict, Depends(common_pagination_parameters)]):
    return {200: "OK"}
