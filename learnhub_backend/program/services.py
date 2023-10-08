from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    query_list_programs,
    query_list_tags,
)

from .schemas import (
    ListProgramsResponseModel,
    ListProgramsCourseModelBody,
    ListProgramsClassModelBody,
    ListTagsResponseModel,
    TagModelBody,
)


# PROGRAMS
def list_programs_response(skip: int = 0, limit: int = 0) -> ListProgramsResponseModel:
    queried_programs = query_list_programs(skip, limit)
    ta = TypeAdapter(
        list[Union[ListProgramsClassModelBody, ListProgramsCourseModelBody]]
    )
    response_body = ListProgramsResponseModel(
        programs=ta.validate_python(queried_programs)
    )
    return response_body


def list_tags_response(skip: int = 0, limit: int = 100) -> ListTagsResponseModel:
    tags_cur = query_list_tags(skip, limit)
    tags = []
    for tag_ in tags_cur:
        tag_["tag_id"] = str(tag_["_id"])
        tag_["tag_name"] = tag_["name"]
        tags.append(tag_)
    ta = TypeAdapter(list[TagModelBody])
    response_body = ListTagsResponseModel(tags=ta.validate_python(tags))
    return response_body
