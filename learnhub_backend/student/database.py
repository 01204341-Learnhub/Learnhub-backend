from pymongo.results import DeleteResult, UpdateResult
from learnhub_backend.student.schemas import PatchStudentRequestModel
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId

from .config import student_type, course_type

from ..dependencies import (
    Exception,
)

def query_list_students(skip: int = 0, limit: int = 100) -> list:
    filter = {"type": student_type}
    students_cursor = db_client.user_coll.find(skip=skip, limit=limit, filter=filter)
    students = []
    for student in students_cursor:
        student["student_id"] = str(student["_id"])
        students.append(student)

    return students


def query_student(student_id: str) -> dict | None:
    filter = {"_id": ObjectId(student_id), "type": student_type}
    student = db_client.user_coll.find_one(filter=filter)
    if student != None:
        student["student_id"] = str(student["_id"])
    return student


def edit_student(student_id: str, request: PatchStudentRequestModel) -> UpdateResult:
    filter = {"type": student_type, "_id": ObjectId(student_id)}

    update_body = {}
    if request.username != None:
        update_body["username"] = request.username
    if request.fullname != None:
        update_body["fullname"] = request.fullname
    if request.profile_pic != None:
        update_body["profile_pic"] = request.profile_pic
    update = {"$set": update_body}

    result = db_client.user_coll.update_one(filter=filter, update=update)
    return result


def remove_student(student_id: str) -> DeleteResult:
    filter = {"type": student_type, "_id": ObjectId(student_id)}

    result = db_client.user_coll.delete_one(filter=filter)
    return result


def query_list_student_course(student_id: str):
    filter = {"type": student_type, "_id": ObjectId(student_id)}
    # TODO: Query course db student list.


# STUDENT COURSE PROGRESS
def query_student_course_progress(student_id: str, course_id: str) -> dict:
    try:
        filter = {"student_id":ObjectId(student_id), "course_id":ObjectId(course_id)}
        student_course_progress = db_client.course_progress_coll.find_one(filter=filter)
        if student_course_progress == None:
            raise Exception.not_found
        for i in range(len(student_course_progress["lessons"])): 
            student_course_progress["lessons"][i]["lesson_id"] = str(student_course_progress["lessons"][i]["lesson_id"])
            student_course_progress["lessons"][i]["chapter_id"] = str(student_course_progress["lessons"][i]["chapter_id"])
    except InvalidId:
        raise Exception.bad_request
    return student_course_progress