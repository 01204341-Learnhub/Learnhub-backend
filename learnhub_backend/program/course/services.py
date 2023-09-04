from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import (
    query_list_course_chapters,
    create_course_chapter,
    query_course_chapter,
    edit_course_chapter,
    delete_course_chapter,
)
from .schemas import (
    ListCourseChaptersModelBody,
    ListCourseChaptersResponseModel,
    PostCourseChaptersRequestModel,
    GetCourseChapterResponseModel,
    PatchCourseChapterRequestModel,
    ListCourseLessonsResponseModel,
    ListCourseLessonsModelBody,
    GetCourseLessonResponseModel,
    PatchCourseLessonRequestModel,
    PostCourseLessonRequestModel,
    PostCourseLessonResponseModel,
)

from .database import (
    edit_course_lesson,
    query_list_course_lessons,
    query_get_course_lesson,
    create_course_lesson,
    remove_course_lesson,
)


# COURSE CHAPTERS
def list_course_chapters_response(course_id: str, skip: int = 0, limit: int = 0):
    queried_chapters = query_list_course_chapters(
        course_id=course_id, skip=skip, limit=limit
    )
    ta = TypeAdapter(list[ListCourseChaptersModelBody])
    response_body = ListCourseChaptersResponseModel(
        chapters=ta.validate_python(queried_chapters)
    )
    return response_body


def add_course_chapter_response(
    course_id: str, chapter_body: PostCourseChaptersRequestModel
) -> dict | None:
    response = create_course_chapter(course_id=course_id, chapter_body=chapter_body)
    if response.inserted_id == None:
        return None
    return {"chapter_id": str(response.inserted_id)}


def get_course_chapter_response(chapter_id: str):
    queried_chapter = query_course_chapter(chapter_id=chapter_id)
    if queried_chapter == None:
        return None
    ta = TypeAdapter(GetCourseChapterResponseModel)
    response_body = GetCourseChapterResponseModel(
        **ta.validate_python(queried_chapter).model_dump()
    )
    return response_body


def edit_course_chapter_response(
    chapter_id: str, chapter_to_edit: PatchCourseChapterRequestModel
):
    response = edit_course_chapter(
        chapter_id=chapter_id, chapter_to_edit=chapter_to_edit
    )
    return response


def delete_course_chapter_response(chapter_id: str, course_id: str) -> int:
    response = delete_course_chapter(chapter_id=chapter_id, course_id=course_id)
    return response


# COURSE LESSON
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


def add_course_lesson_request(
    course_id: str, chapter_id: str, request: PostCourseLessonRequestModel
) -> PostCourseLessonResponseModel | None:
    object_id = create_course_lesson(course_id, chapter_id, request)
    response_body = PostCourseLessonResponseModel(lesson_id=object_id)
    return response_body


def edit_course_lesson_request(
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
