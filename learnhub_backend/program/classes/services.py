from datetime import datetime
from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import UpdateResult

from learnhub_backend.dependencies import GenericOKResponse

from .database import (
    query_list_classes,
    get_teacher_by_id,
    query_list_tags_by_id,
    query_class,
    edit_assignment,
)
from .schemas import (
    ListClassesModelBody,
    ListClassesResponseModel,
    GetClassResponseModel,
    PatchAssignmentRequestModel,
)

from ...dependencies import Exception


# CLASSES
def list_classes_response(skip: int, limit: int) -> ListClassesResponseModel:
    classes_corsor = query_list_classes(skip=skip, limit=limit)
    quried_classes = []
    for class_ in classes_corsor:
        class_["class_id"] = str(class_["_id"])
        class_["teacher"] = get_teacher_by_id(str(class_["teacher_id"]))
        class_["tags"] = query_list_tags_by_id(class_["tags"])
        class_["registration_ended_date"] = int(
            datetime.timestamp(class_["registration_ended_date"])
        )
        class_["open_time"] = int(datetime.timestamp(class_["open_time"]))
        class_["class_ended_date"] = int(datetime.timestamp(class_["class_ended_date"]))
        quried_classes.append(class_)

    ta = TypeAdapter(list[ListClassesModelBody])
    response_body = ListClassesResponseModel(classes=ta.validate_python(quried_classes))
    return response_body


def get_class_response(class_id: str) -> GetClassResponseModel:
    class_ = query_class(class_id=class_id)
    if class_ == None:
        raise Exception.not_found

    class_["class_id"] = str(class_["_id"])
    class_["teacher"] = get_teacher_by_id(str(class_["teacher_id"]))
    class_["tags"] = query_list_tags_by_id(class_["tags"])
    class_["registration_ended_date"] = int(
        datetime.timestamp(class_["registration_ended_date"])
    )
    class_["open_time"] = int(datetime.timestamp(class_["open_time"]))
    class_["class_ended_date"] = int(datetime.timestamp(class_["class_ended_date"]))

    return GetClassResponseModel(**class_)


# ASSIGNMENTS
def patch_assignment_request(
    class_id: str, assignment_id: str, patch_body: PatchAssignmentRequestModel
):
    response = edit_assignment(
        class_id=class_id, assignment_id=assignment_id, patch_body_=patch_body
    )
    return GenericOKResponse
