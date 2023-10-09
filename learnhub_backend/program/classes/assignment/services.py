from datetime import datetime
from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import UpdateResult

from ....dependencies import GenericOKResponse

from .schemas import (
    PatchAssignmentRequestModel,
)

from .database import (
    edit_assignment,
)


# ASSIGNMENTS
def patch_assignment_request(
    class_id: str, assignment_id: str, patch_body: PatchAssignmentRequestModel
):
    response = edit_assignment(
        class_id=class_id, assignment_id=assignment_id, patch_body_=patch_body
    )
    return GenericOKResponse
