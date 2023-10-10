from typing import Annotated, Union
from pydantic import TypeAdapter
from pymongo.results import UpdateResult

from learnhub_backend.dependencies import GenericOKResponse
from learnhub_backend.student.database import query_student

from .database import (
    create_course,
    query_course,
    query_list_tags_by_id,
    query_teacher_by_id,
    query_list_courses,
    query_list_course_chapters,
    create_course_chapter,
    query_course_chapter,
    edit_course_chapter,
    delete_course_chapter,
    edit_course_lesson,
    query_list_course_lessons,
    query_course_lesson,
    create_course_lesson,
    remove_course_lesson,
    review_course,
    student_is_own_program,
)
from .schemas import (
    GetCourseResponseModel,
    PatchCourseReviewRequestModel,
    PatchCourseReviewResponseModel,
    PostCourseRequestModel,
    PostCourseResponseModel,
    TagModelBody,
    TeacherModelBody,
    ListCoursesModelBody,
    ListCoursesResponseModel,
    ListCourseChaptersModelBody,
    ListCourseChaptersResponseModel,
    PostCourseChapterRequestModel,
    PostCourseChapterResponseModel,
    GetCourseChapterResponseModel,
    PatchCourseChapterRequestModel,
    ListCourseLessonsResponseModel,
    ListCourseLessonsModelBody,
    GetCourseLessonResponseModel,
    PatchCourseLessonRequestModel,
    PostCourseLessonRequestModel,
    PostCourseLessonResponseModel,
)

from ...dependencies import (
    Exception,
    student_type,
    teacher_type,
    course_type,
    class_type,
)


# COURSE
def list_courses_response(skip: int = 0, limit: int = 100):
    queried_courses = query_list_courses(skip, limit)
    list_courses_response = list()
    course_response = dict()
    for course in queried_courses:
        course_response["course_id"] = course["course_id"]
        course_response["name"] = course["name"]
        course_response["rating"] = course["rating"]
        course_response["review_count"] = course["review_count"]
        course_response["price"] = course["price"]
        course_response["course_pic"] = course["course_pic"]
        course_response["difficulty_level"] = course["difficulty_level"]

        # teacher
        teacher = query_teacher_by_id(course["teacher_id"])
        if teacher == None:
            raise Exception.internal_server_error  # No teacher was found
        teacher["teacher_id"] = str(teacher["_id"])
        teacher["teacher_name"] = teacher["fullname"]
        course_response["teacher"] = TeacherModelBody(**teacher)

        # tags
        tags = []
        tags_cursor = query_list_tags_by_id(course["tags"])
        for tag in tags_cursor:
            tag["tag_id"] = str(tag["_id"])
            tag["tag_name"] = tag["name"]
            tags.append(TagModelBody(**tag))
        course_response["tags"] = tags

        list_courses_response.append(ListCoursesModelBody(**course_response))
    return ListCoursesResponseModel(courses=list_courses_response)


def add_course_request(request: PostCourseRequestModel) -> PostCourseResponseModel:
    result = create_course(request)
    response_body = PostCourseResponseModel(course_id=str(result.inserted_id))
    return response_body


def get_course_response(course_id: str):
    course = query_course(course_id)
    if course == None:
        raise Exception.not_found

    course["course_id"] = str(course["_id"])

    # teacher
    teacher = query_teacher_by_id(course["teacher_id"])
    if teacher == None:
        raise Exception.internal_server_error  # No teacher was found
    teacher["teacher_id"] = str(teacher["_id"])
    teacher["teacher_name"] = teacher["fullname"]
    course["teacher"] = TeacherModelBody(**teacher)

    # tags
    tags_cursor = query_list_tags_by_id(course["tags"])
    tags = []
    for tag in tags_cursor:
        tag["tag_id"] = str(tag["_id"])
        tag["tag_name"] = tag["name"]
        tags.append(TagModelBody(**tag))
    course["tags"] = tags

    return GetCourseResponseModel(**course)


def patch_course_review_request(
    course_id: str, request: PatchCourseReviewRequestModel
) -> PatchCourseReviewResponseModel:
    if not student_is_own_program(request.student_id, course_type, course_id):
        err = Exception.not_found
        err.__setattr__("detail", "Course's not owned by the request's student")
        raise err

    assert request.rating >= 0 and request.rating <= 5

    review_id = review_course(course_id, request.student_id, request.rating)
    return PatchCourseReviewResponseModel(review_id=review_id)


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


def add_course_chapter_request(
    course_id: str, chapter_body: PostCourseChapterRequestModel
) -> PostCourseChapterResponseModel:
    result = create_course_chapter(course_id=course_id, chapter_body=chapter_body)
    if result.inserted_id == None:
        raise Exception.bad_request
    response_body = PostCourseChapterResponseModel(chapter_id=str(result.inserted_id))

    return response_body


def get_course_chapter_response(chapter_id: str):
    queried_chapter = query_course_chapter(chapter_id=chapter_id)
    if queried_chapter == None:
        raise Exception.not_found
    response_body = GetCourseChapterResponseModel(**queried_chapter)
    return response_body


def edit_course_chapter_response(
    chapter_id: str, chapter_to_edit: PatchCourseChapterRequestModel
):
    response = edit_course_chapter(
        chapter_id=chapter_id, chapter_to_edit=chapter_to_edit
    )
    return GenericOKResponse


def delete_course_chapter_response(chapter_id: str, course_id: str):
    delete_course_chapter(chapter_id=chapter_id, course_id=course_id)
    return GenericOKResponse


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
    quried_lesson = query_course_lesson(course_id, chapter_id, lesson_id)
    if quried_lesson == None:
        raise Exception.not_found
    if "quiz_id" in quried_lesson:
        quried_lesson["quiz_id"] = str(quried_lesson["quiz_id"])
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
):
    edit_course_lesson(course_id, chapter_id, lesson_id, request)
    return GenericOKResponse


def delete_course_lesson_request(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
):
    remove_course_lesson(course_id, chapter_id, lesson_id)
    return GenericOKResponse
