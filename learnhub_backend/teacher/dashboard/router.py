from fastapi import APIRouter, Depends
from typing import Annotated, Union

from learnhub_backend.teacher.dashboard.schemas import (
    GetTeacherDashboardResponseModel,
)


from .services import get_teacher_dashboard_response

from ...dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)


router = APIRouter(
    prefix="/users/teachers",
    tags=["teacher"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


@router.get(
    "/{teacher_id}/dashboard",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetTeacherDashboardResponseModel,
)
def get_teacher_dashboard(teacher_id: str):
    response_body = get_teacher_dashboard_response(teacher_id)
    return response_body
