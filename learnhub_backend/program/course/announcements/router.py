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
    PostCourseAnnouncementResponseModel,
    GetCourseAnnouncementResponseModel,
)
from .services import (
    create_course_announcements_request,
    list_course_announcements_response,
    get_course_announcement_response,
    patch_course_annoucement_request,
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
    response_model=PostCourseAnnouncementResponseModel,
)
def create_course_annoucement(
    course_id: str, annoucement_body: PostCourseAnnouncementRequestModel
):
    response_body = create_course_announcements_request(course_id, annoucement_body)
    return response_body


@router.get(
    "/{course_id}/announcements/{announcement_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetCourseAnnouncementResponseModel,
)
def get_course_annoucement(course_id: str, announcement_id: str):
    response_body = get_course_announcement_response(
        course_id=course_id, announcement_id=announcement_id
    )
    return response_body

@router.patch(
    "/{course_id}/announcements/{announcement_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=None,
)
def patch_course_annoucement(course_id: str, announcement_id: str):
    #TODO: implement patch_course_annoucement
    response_body = patch_course_annoucement_request(
        course_id=course_id, announcement_id=announcement_id
    )
    return response_body
