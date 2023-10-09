from fastapi import APIRouter, Depends
from typing import Annotated, Union

from ....dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .schemas import (
    PatchAssignmentRequestModel,
)

from .services import (
    patch_assignment_request,
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


# ASSIGNMENTS
@router.patch(
    "/{class_id}/assignments/{assignment_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def patch_assignment(
    class_id: str, assignment_id: str, patch_body: PatchAssignmentRequestModel
):
    response_body = patch_assignment_request(
        class_id=class_id, assignment_id=assignment_id, patch_body=patch_body
    )
    return response_body
