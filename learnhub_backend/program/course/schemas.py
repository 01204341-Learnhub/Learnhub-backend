from typing import Optional, Union
from pydantic import BaseModel, HttpUrl


class TeacherModelBody(BaseModel):
    teacher_id: str
    teacher_name: str


class TagModelBody(BaseModel):
    tag_id: str
    tag_name: str


# COURSE
class ListCoursesModelBody(BaseModel):
    course_id: str
    name: str
    teacher: TeacherModelBody
    tags: list[TagModelBody]
    rating: float
    review_count: int
    price: float
    course_pic: HttpUrl


class ListCoursesResponseModel(BaseModel):
    courses: list[ListCoursesModelBody]


class PostCourseRequestModel(BaseModel):
    name: str
    teacher_id: str
    course_pic: HttpUrl
    description: str
    course_objective: list[str]
    tag_ids: list[str]
    course_requirement: str
    difficulty_level: str
    price: float


class PostCourseResponseModel(BaseModel):
    course_id: str


# COURSE CHAPTERS
class ListCourseChaptersModelBody(BaseModel):
    chapter_id: str
    chapter_num: int
    name: str
    lesson_count: int
    chapter_length: int


class ListCourseChaptersResponseModel(BaseModel):
    chapters: list[ListCourseChaptersModelBody]


class PostCourseChapterRequestModel(BaseModel):
    name: str
    description: str


class PostCourseChapterResponseModel(BaseModel):
    chapter_id: str


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
