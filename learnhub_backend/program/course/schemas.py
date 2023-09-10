from typing import Optional, Union
from pydantic import BaseModel, HttpUrl


# COURSE CHAPTERS


    
    
class ListCourseChaptersModelBody(BaseModel):
    chapter_id: str
    chapter_num: int
    name: str


class ListCourseChaptersResponseModel(BaseModel):
    chapters: list[ListCourseChaptersModelBody]


class PostCourseChaptersRequestModel(BaseModel):
    name: str


class GetCourseChapterResponseModel(BaseModel):
    chapter_id: str
    course_id: str
    chapter_num: int
    name: str


class PatchCourseChapterRequestModel(BaseModel):
    name: Optional[str] = None


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
    
#bun start
class ListCourseStudentsModelBody(BaseModel):
    student_id: str
    name: str
    profile_pic: str

class ListCourseModelBody(BaseModel):
    course_id: str
    name: str
    teacher: {
        "teacher_id": str,
        "teacher_name": str
    }
    rating: int
    review_count: int
    price: int
    course_pic: HttpUrl


class ListCourseResponseModel(BaseModel):
    course: list[ListCourseModelBody]
    
class ListCourseIdResponseModel(BaseException):
    course_id: str
    name: str
    course_pic: HttpUrl
    description: str
    course_objective: list[str]
    course_requirement: str
    difficulty_level: str
    rating: float
    review_count: int
    student_count: int
    teacher: {
        "teacher_id": str,
        "teacher_name": str
    }
    price: int
    total_video_length: int
    chapter_count: int
    quiz_count: int
    file_count: int
    
class ListCourseStudentsResponseModel(BaseException):
    course_students: list[ListCourseStudentsModelBody]
    
class PostCourseRequestModel(BaseException):
    teacher_id: str
    name: str
    course_pic: HttpUrl
    description: str
    course_objective: list[str]
    course_requirement: str
    difficulty_level: str
    price: int