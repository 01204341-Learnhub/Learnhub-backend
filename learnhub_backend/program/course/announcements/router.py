from typing import Annotated
from fastapi import APIRouter, Depends

from learnhub_backend.dependencies import (
    GenericOKResponse,
    common_pagination_parameters,
    Exception,
)
from .schemas import (
    ListCourseAnnouncementsResponseModel,
    PostCourseAnnouncementRequestModel,
)
from .services import (
    create_course_announcements_response,
    list_course_announcements_response,
)


router = APIRouter(
    prefix="/programs/courses",
    tags=["announcements"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


@router.get(
    "/{course_id}/announcements",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListCourseAnnouncementsResponseModel,
)
def list_course_annoucements(course_id: str, common_paginations: common_page_params):
    response_body = list_course_announcements_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
        course_id=course_id,
    )
    return response_body


@router.post(
    "/{course_id}/announcements",
    status_code=200,
    response_model_exclude_none=True,
)
def create_course_annoucement(
    course_id: str, annoucement_body: PostCourseAnnouncementRequestModel
):
    created_id = create_course_announcements_response(course_id, annoucement_body)
    return {"announcement_id": created_id}
