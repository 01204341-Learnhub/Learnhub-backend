from fastapi import APIRouter, Depends
from typing import Annotated, Union


from ...dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)


from .services import (
    get_student_dashboard_response,
)
from .schemas import (
    GetStudentDashboard,
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


@router.get(
    "/{student_id}/dashboard",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetStudentDashboard,
)
def get_student_dashboard(student_id: str):
    response_body = get_student_dashboard_response(student_id)
    return response_body
