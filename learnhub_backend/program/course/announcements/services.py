from pydantic import TypeAdapter
from datetime import datetime
from .database import (
    create_course_announcement,
    list_course_announcement,
    query_course_announcement,
)
from .schemas import (
    ListCourseAnnouncementsModelBody,
    ListCourseAnnouncementsResponseModel,
    PostCourseAnnouncementRequestModel,
    PostCourseAnnouncementResponseModel,
    GetCourseAnnouncementResponseModel,
)


def list_course_announcements_response(
    course_id: str, skip: int = 0, limit: int = 100
) -> ListCourseAnnouncementsResponseModel:
    quried_annoucements = list_course_announcement(course_id, skip, limit)
    ta = TypeAdapter(list[ListCourseAnnouncementsModelBody])
    response_body = ListCourseAnnouncementsResponseModel(
        annoucements=ta.validate_python(quried_annoucements)
    )
    return response_body


def create_course_announcements_request(
    course_id: str, request_body: PostCourseAnnouncementRequestModel
) -> PostCourseAnnouncementResponseModel:
    created_id = create_course_announcement(
        course_id=course_id, announcement_body=request_body
    )
    response_body = PostCourseAnnouncementResponseModel(announcement_id=created_id)
    return response_body


def get_course_announcement_response(course_id: str, announcement_id: str)->GetCourseAnnouncementResponseModel:
    response_body = query_course_announcement(
        course_id=course_id, announcement_id=announcement_id
    )
    response_body["announcement_id"] = str(response_body["_id"])
    response_body["teacher"] = str(
        response_body["teacher_id"]
    )  # TODO: change to TeacherModelBody
    response_body["last_edit"] = int(datetime.timestamp(response_body["last_edit"]))

    return GetCourseAnnouncementResponseModel(**response_body)


def patch_course_annoucement_request(course_id: str, announcement_id: str):
    #TODO: implement patch_course_annoucement_request
    pass
