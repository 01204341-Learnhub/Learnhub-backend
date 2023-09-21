from typing import Optional, Union
from pydantic import BaseModel, HttpUrl


# COURSE CHAPTERS
class ListCourseChaptersModelBody(BaseModel):
    chapter_id: str
    chapter_num: int
    name: str
    lesson_count: int
    chapter_length: int


class ListCourseChaptersResponseModel(BaseModel):
    chapters: list[ListCourseChaptersModelBody]


class PostCourseChaptersRequestModel(BaseModel):
    name: str
    description: str


class GetCourseChapterResponseModel(BaseModel):
    chapter_id: str
    course_id: str
    chapter_num: int
    name: str
    description: str


class PatchCourseChapterRequestModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


## Lessons
class GetCourseLessonResponseModel(BaseModel):
    lesson_id: str
    lesson_num: int
    name: str
    lesson_type: str
    description: str
    src: HttpUrl
    # TODO: only return progress, If student_id is attached.
    progress: float | None = None


class ListCourseLessonsModelBody(BaseModel):
    lesson_id: str
    lesson_num: int
    name: str
    lesson_type: str
    video_length: int | None = None  # only return if lesson type = 'video'


class ListCourseLessonsResponseModel(BaseModel):
    lessons: list[ListCourseLessonsModelBody]


class PostCourseLessonRequestModel(BaseModel):
    name: str
    description: str
    src: HttpUrl


class PostCourseLessonResponseModel(BaseModel):
    lesson_id: str


class PatchCourseLessonRequestModel(BaseModel):
    name: str | None = None
    description: str | None = None
    src: HttpUrl | None = None
