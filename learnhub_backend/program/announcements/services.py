from pydantic import TypeAdapter
from learnhub_backend.program.announcements.database import create_course_announcement, list_course_announcement
from learnhub_backend.program.announcements.schemas import ListCourseAnnouncementsModelBody, ListCourseAnnouncementsResponseModel, PostCourseAnnouncementRequestModel


def list_course_announcements_response(
    course_id: str, skip: int = 0, limit: int = 100
) -> ListCourseAnnouncementsResponseModel:
    quried_annoucements = list_course_announcement(course_id, skip, limit)
    ta = TypeAdapter(list[ListCourseAnnouncementsModelBody])
    response_body = ListCourseAnnouncementsResponseModel(
        annoucements=ta.validate_python(quried_annoucements)
    )
    return response_body

def create_course_announcements_response(course_id: str, requestBody: PostCourseAnnouncementRequestModel):
    created_id = create_course_announcement(course_id, requestBody)
    return created_id
