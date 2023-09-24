from fastapi import APIRouter, Depends
from typing import Annotated, Union
from ...dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    service_placeholder
)

from .schemas import (
    placeholder
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

@router.get("/")
def test():
    return {"Hello": "World"}