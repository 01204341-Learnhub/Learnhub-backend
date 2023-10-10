from fastapi import APIRouter, Depends
from typing import Annotated, Union

from ...dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
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
