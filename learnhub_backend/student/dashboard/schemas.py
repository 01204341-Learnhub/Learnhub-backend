from typing import Optional, Union
from pydantic import BaseModel, HttpUrl, validator


# AUX
class TeacherModelBody(BaseModel):
    teacher_id: str
    teacher_name: str
    profile_pic: HttpUrl


class ClassInfoModelBody(BaseModel):
    class_id: str
    class_name: str
    class_pic: HttpUrl


class CourseInfoModelBody(BaseModel):
    course_id: str
    course_name: str


class SubmissionModelBody(BaseModel):
    submission_status: str  # check | uncheck | unsubmit
    submission_date: int


class ClassScheduleModelBody(BaseModel):
    start: int
    end: int


# DASHBOARD
class StudentClassDashboardModelBody(BaseModel):
    class_info: ClassInfoModelBody
    teacher: TeacherModelBody
    schedules: list[ClassScheduleModelBody]


class StudentAssignmentDashboardModelBody(BaseModel):
    assignment_name: str
    assignment_id: str
    class_info: ClassInfoModelBody
    due_date: int
    status: str  # open | closed
    submission: SubmissionModelBody


class StudentAnnouncementDashboardModelBody(BaseModel):
    announcement_id: str
    course_info: CourseInfoModelBody
    teacher: TeacherModelBody
    name: str
    last_edit: int
    text: str


class GetStudentDashboard(BaseModel):
    classes: list[StudentClassDashboardModelBody]
    assignments: list[StudentAssignmentDashboardModelBody]
    announcements: list[StudentAnnouncementDashboardModelBody]
