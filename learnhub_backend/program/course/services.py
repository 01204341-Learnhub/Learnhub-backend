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
    ListCourseResponseModel, #123
    GetCourseIdResponseModel, #123
    ListCourseStudentsResponseModel, #123
    PostCourseRequestModel, #123
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
    PatchCourseRequestModel,
    ListCourseModelBody,
    ListCourseStudentsModelBody,
)

from .database import (
    edit_course_lesson,
    query_list_course_lessons,
    query_get_course_lesson,
    create_course_lesson,
    remove_course_lesson,
    edit_course,
    remove_course,
    create_course,
    query_get_course_id,
    query_list_course,
    query_list_course_students,
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

#bun start here
def edit_course_response(
    course_id: str,
    request: PatchCourseRequestModel,
) -> int:
    modified_count = edit_course(course_id, request)
    return modified_count


def delete_course_response(
    course_id: str,
) -> int:
    delete_count = remove_course(course_id)
    return delete_count

def add_course_response(
    course_body: PostCourseRequestModel
) -> dict | None:
    response = create_course(course_body=course_body)
    if response.inserted_id == None:
        return None
    return {"course_id": str(response.inserted_id)}

def get_course_id_response(
    course_id: str
) -> GetCourseIdResponseModel | None:
    try:
        quried_course_id = query_get_course_id(course_id)
    except:
        return None
    if quried_course_id == None:
        return None
    response_body = GetCourseIdResponseModel(**quried_course_id)
    return response_body

def list_course_response(
    skip: int = 0, limit: int = 0
) -> ListCourseResponseModel:
    quried_course = query_list_course(skip, limit)
    ta = TypeAdapter(list[ListCourseModelBody])
    response_body = ListCourseResponseModel(
        course=ta.validate_python(quried_course)
    )
    return response_body

def list_course_students_response(
    course_id: str, skip: int = 0, limit: int = 0
) -> ListCourseStudentsResponseModel:
    quried_students = query_list_course_students(course_id, skip, limit)
    ta = TypeAdapter(list[ListCourseStudentsModelBody])
    response_body = ListCourseStudentsResponseModel(
        students=ta.validate_python(quried_students)
    )
    return response_body