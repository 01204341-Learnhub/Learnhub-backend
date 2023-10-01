from typing import Annotated
from fastapi import APIRouter, Depends

from learnhub_backend.dependencies import (
    GenericOKResponse,
    common_pagination_parameters,
    Exception,
)
from .schemas import (
    PlaceHolderModel
)
from .services import (
    place_holder_service,
)


router = APIRouter(
    prefix="/quizzes",
    tags=["quizzes"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


@router.get(
    "/{quiz_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=None,
)
def get_quiz(quiz_id : str):
    response_body = place_holder_service(
        quiz_id=quiz_id ,
    )
    return response_body
