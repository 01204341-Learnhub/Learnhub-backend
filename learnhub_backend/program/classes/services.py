from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import UpdateResult

from learnhub_backend.dependencies import GenericOKResponse

from .database import (
    db_placeholder,
    query_list_classes,
)
from .schemas import placeholder, ListClassesModelBody, ListClassesResponseModel

from ...dependencies import Exception


def service_placeholder():
    return 0


# CLASSES
def list_classes_response(skip: int, limit: int): # TODO: add return type
    classes_corsor = query_list_classes(skip=skip, limit=limit)
    quried_classes = []
    for class_ in classes_corsor:
        class_["class_id"] = str(class_["_id"])
        # TODO: change teacher_id to TeacherModelBody
        class_["teacher"] = str(class_["teacher_id"])
        for i in range(len(class_["tags"])):
            # TODO: change teacher_id to TagModelBody
            class_["tags"][i] = str(class_["tags"][i])
        quried_classes.append(class_)
    
    ta = TypeAdapter(list[ListClassesModelBody])
    response_body = ListClassesResponseModel(classes=ta.validate_python(quried_classes))
    return response_body
