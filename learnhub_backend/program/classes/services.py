from datetime import datetime
from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import UpdateResult

from learnhub_backend.dependencies import GenericOKResponse

from .database import (
    create_class,
    edit_class,
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
    PatchClassRequestModel,
    PostClassRequestModel,
    PostClassResponseModel,
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
        class_["open_date"] = int(datetime.timestamp(class_["open_date"]))
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
    class_["open_date"] = int(datetime.timestamp(class_["open_date"]))
    class_["class_ended_date"] = int(datetime.timestamp(class_["class_ended_date"]))
    for i in range(len(class_["schedules"])):
        print(class_["schedules"][i]["start"])
        class_["schedules"][i]["start"] = int(datetime.timestamp(class_["schedules"][i]["start"]))
        class_["schedules"][i]["end"] = int(datetime.timestamp(class_["schedules"][i]["end"]))

    return GetClassResponseModel(**class_)


def post_class_request(request: PostClassRequestModel) -> PostClassResponseModel:
    class_id = create_class(request)
    return PostClassResponseModel(class_id=class_id)


def patch_class_request(class_id: str, request: PatchClassRequestModel):
    edit_class(class_id, request)
    return GenericOKResponse


# ASSIGNMENTS
def patch_assignment_request(
    class_id: str, assignment_id: str, patch_body: PatchAssignmentRequestModel
):
    response = edit_assignment(
        class_id=class_id, assignment_id=assignment_id, patch_body_=patch_body
    )
    return GenericOKResponse
