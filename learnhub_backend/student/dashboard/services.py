from datetime import datetime, timezone, tzinfo
from typing import Annotated, Union
from bson.objectid import ObjectId
from pydantic import HttpUrl, TypeAdapter
from pymongo.results import DeleteResult, UpdateResult

from learnhub_backend.dependencies import (
    GenericOKResponse,
    Exception,
    class_type,
    course_type,
    student_type,
    teacher_type,
    get_timestamp_from_datetime,
)

from .schemas import (
    ClassInfoModelBody,
    CourseInfoModelBody,
    GetStudentDashboard,
    StudentAnnouncementDashboardModelBody,
    StudentAssignmentDashboardModelBody,
    StudentClassDashboardModelBody,
    SubmissionModelBody,
    TeacherModelBody,
    ClassScheduleModelBody,
)

from .database import (
    query_announcements_by_course,
    query_assignments_by_class,
    query_class,
    query_course,
    query_student,
    query_submission_by_assignment,
    query_teacher,
)

from .config import (
    _Program,
)


# AUX
def _get_teacher_info(teacher_id: str) -> TeacherModelBody:
    teacher = query_teacher(teacher_id)
    if teacher == None:
        err = Exception.not_found
        err.__setattr__("detail", "Teacher not found")
        raise err
    return TeacherModelBody(
        teacher_id=teacher_id,
        teacher_name=teacher["fullname"],
        profile_pic=HttpUrl(teacher["profile_pic"]),
    )


# DASHBOARD
def get_student_dashboard_response(student_id: str) -> GetStudentDashboard:
    student = query_student(student_id)
    if student == None:
        err = Exception.not_found
        err.__setattr__("detail", "Student not found")
        raise err

    classes: list[StudentClassDashboardModelBody] = []
    assignments: list[StudentAssignmentDashboardModelBody] = []
    announcements: list[StudentAnnouncementDashboardModelBody] = []

    for program_ in student["owned_programs"]:
        program_ = _Program(program_["program_id"], program_["type"])

        if program_.type == class_type:
            # CLASS
            class_ = query_class(program_.program_id)
            if class_ == None:
                err = Exception.not_found
                err.__setattr__("detail", "Class not found")
                raise err

            teacher = _get_teacher_info(str(class_["teacher_id"]))
            class_info = ClassInfoModelBody(
                class_id=str(class_["_id"]), class_name=class_["name"]
            )

            classes.append(
                StudentClassDashboardModelBody(
                    class_info=class_info,
                    teacher=teacher,
                    schedules=[
                        ClassScheduleModelBody(
                            start=get_timestamp_from_datetime(_sched["start"]),
                            end=get_timestamp_from_datetime(_sched["end"]),
                        )
                        for _sched in class_["schedules"]
                    ],
                )
            )

            # ASSIGNMENT
            assignments_cur = query_assignments_by_class(str(class_["_id"]))
            for assg_ in assignments_cur:
                _submission = query_submission_by_assignment(str(assg_["_id"]))
                if _submission == None:
                    err = Exception.not_found
                    err.__setattr__("detail", "Submission not found")
                    raise err
                _assignment = StudentAssignmentDashboardModelBody(
                    assignment_name=assg_["name"],
                    assignment_id=str(assg_["_id"]),
                    class_info=ClassInfoModelBody(
                        class_id=str(class_["_id"]), class_name=class_["name"]
                    ),
                    due_date=get_timestamp_from_datetime(assg_["due_date"]),
                    status=assg_["status"],
                    submission=SubmissionModelBody(
                        submission_status=_submission["status"],
                        submission_date=get_timestamp_from_datetime(
                            _submission["submission_date"]
                        ),
                    ),
                )
                assignments.append(_assignment)
        elif program_.type == course_type:
            # COURSE
            course_ = query_course(program_.program_id)
            if course_ == None:
                err = Exception.not_found
                err.__setattr__("detail", "Course not found")
                raise err
            teacher_ = _get_teacher_info(str(course_["teacher_id"]))
            announcements_cur = query_announcements_by_course(str(course_["_id"]))
            for announce_ in announcements_cur:
                _announcement = StudentAnnouncementDashboardModelBody(
                    name=announce_["name"],
                    announcement_id=str(announce_["_id"]),
                    course_info=CourseInfoModelBody(
                        course_id=str(course_["_id"]), course_name=course_["name"]
                    ),
                    teacher=teacher_,
                    last_edit=get_timestamp_from_datetime(announce_["last_edit"]),
                    text=announce_["text"],
                )
                announcements.append(_announcement)
    # assign response
    response = GetStudentDashboard(
        classes=classes, assignments=assignments, announcements=announcements
    )
    return response
