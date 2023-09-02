from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    edit_course_lesson,
    query_list_programs,
    query_list_course_lessons,
    query_get_course_lesson,
    create_course_lesson,
    remove_course_lesson,
)
from .schemas import (
    ListProgramsResponseModel,
    ListProgramsCourseModelBody,
    ListProgramsClassModelBody,
    ListCourseLessonsResponseModel,
    ListCourseLessonsModelBody,
    GetCourseLessonResponseModel,
    PatchCourseLessonRequestModel,
    PostCourseLessonRequestModel,
    PostCourseLessonResponseModel,
)


# lesson
def list_programs_response(skip: int = 0, limit: int = 0) -> ListProgramsResponseModel:
    queried_programs = query_list_programs(skip, limit)
    ta = TypeAdapter(
        list[Union[ListProgramsClassModelBody, ListProgramsCourseModelBody]]
    )
    response_body = ListProgramsResponseModel(
        programs=ta.validate_python(queried_programs)
    )
    return response_body


def list_course_lessons_response(
    course_id: str, chapter_id: str, skip: int = 0, limit: int = 0
) -> ListCourseLessonsResponseModel:
    quried_lessons = query_list_course_lessons(course_id, chapter_id, skip, limit)
    ta = TypeAdapter(list[ListCourseLessonsModelBody])
    response_body = ListCourseLessonsResponseModel(
        lessons=ta.validate_python(quried_lessons)
    )
    return response_body


def get_course_lesson_response(
    course_id: str, chapter_id: str, lesson_id: str
) -> GetCourseLessonResponseModel | None:
    try:
        quried_lesson = query_get_course_lesson(course_id, chapter_id, lesson_id)
    except:
        return None
    if quried_lesson == None:
        return None
    response_body = GetCourseLessonResponseModel(**quried_lesson)
    return response_body


def post_course_lesson_request(
    course_id: str, chapter_id: str, request: PostCourseLessonRequestModel
) -> PostCourseLessonResponseModel | None:
    object_id = create_course_lesson(course_id, chapter_id, request)
    response_body = PostCourseLessonResponseModel(lesson_id=object_id)
    return response_body


def patch_course_lesson_request(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
    request: PatchCourseLessonRequestModel,
) -> int:
    modified_count = edit_course_lesson(course_id, chapter_id, lesson_id, request)
    return modified_count


def delete_course_lesson_request(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
) -> int:
    delete_count = remove_course_lesson(course_id, chapter_id, lesson_id)
    return delete_count
