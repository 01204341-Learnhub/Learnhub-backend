from typing import Annotated
from fastapi import APIRouter, Depends

from learnhub_backend.dependencies import (
    GenericOKResponse,
    common_pagination_parameters,
    Exception,
)
from .schemas import (
    GetQuizResponseModel,
    GetQuizResultResponseModel,
)
from .services import (
    get_quiz_response,
    get_quiz_result_response,
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
    response_model=GetQuizResponseModel,
)
def get_quiz(quiz_id : str):
    response_body = get_quiz_response(
        quiz_id=quiz_id ,
    )
    return response_body


@router.get(
    "/{quiz_id}/result",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetQuizResultResponseModel,
)
def get_quiz_result(quiz_id : str, student_id : str):
    response_body = get_quiz_result_response(
        quiz_id=quiz_id ,student_id=student_id
    )
    return response_body
