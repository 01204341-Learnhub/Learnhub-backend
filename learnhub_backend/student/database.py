from pymongo.results import DeleteResult, UpdateResult
from learnhub_backend.student.schemas import (
    PatchStudentRequestModel,
    LessonProgressModelBody,
    PatchStudentConfigRequestModel,
    GetStudentConfigResponseModel
)
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId

from .config import student_type, course_type

from ..dependencies import (
    Exception,
)
from pymongo import ReturnDocument


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
        # find total lessons in course
        total_lessons_filter = {"_id": ObjectId(course_id)}
        total_lessons_projection = {"video_count": 1, "quiz_count": 1, "file_count": 1}
        total_lessons_res = db_client.course_coll.find_one(filter=total_lessons_filter, projection=total_lessons_projection)
        if total_lessons_res == None:
            raise Exception.not_found
        total_lessons = (
            total_lessons_res["video_count"]
            + total_lessons_res["quiz_count"]
            + total_lessons_res["file_count"]
        )

        # find student course progress
        filter = {"student_id": ObjectId(student_id), "course_id": ObjectId(course_id)}
        student_course_progress = db_client.course_progress_coll.find_one(filter=filter)
        if student_course_progress == None:
            raise Exception.not_found
        for i in range(len(student_course_progress["lessons"])):
            student_course_progress["lessons"][i]["lesson_id"] = str(
                student_course_progress["lessons"][i]["lesson_id"]
            )
            student_course_progress["lessons"][i]["chapter_id"] = str(
                student_course_progress["lessons"][i]["chapter_id"]
            )
        student_course_progress["progress"] = (student_course_progress["finished_count"] / total_lessons) * 100
    except InvalidId:
        raise Exception.bad_request
    return student_course_progress


def edit_student_course_progress(
    student_id: str, course_id: str, requested_lesson: LessonProgressModelBody
):
    try:
        # find total lessons in course
        total_lessons_filter = {"_id": ObjectId(course_id)}
        total_lessons_projection = {"video_count": 1, "quiz_count": 1, "file_count": 1}
        total_lessons_res = db_client.course_coll.find_one(filter=total_lessons_filter, projection=total_lessons_projection)
        if total_lessons_res == None:
            raise Exception.not_found
        total_lessons = (
            total_lessons_res["video_count"]
            + total_lessons_res["quiz_count"]
            + total_lessons_res["file_count"]
        )

        # check if lesson is finished already before updating
        update_filter = {
            "student_id": ObjectId(student_id),
            "course_id": ObjectId(course_id),
        }
        check_res = db_client.course_progress_coll.find_one( filter=update_filter)
        if check_res == None:
            raise Exception.not_found
        les_finished_already = False
        for lesson in check_res["lessons"]:
            if lesson["lesson_id"] == ObjectId(requested_lesson.lesson_id) and lesson["chapter_id"] == ObjectId(requested_lesson.chapter_id):
                if lesson["finished"] == True:
                    les_finished_already = True
                    break
        
        # only increment finished_count if lesson is finished (in request) and not finished already(in DB)
        if requested_lesson.finished == True and les_finished_already == False:
            finished_count_inc = 1
        elif requested_lesson.finished == False and les_finished_already == True: # decrement finished_count if user unfinish lesson
            finished_count_inc = -1
        else:
            finished_count_inc = 0
        
        # check if course is finished after updating
        if check_res["finished_count"] + finished_count_inc == total_lessons:
            course_finished = True
        else: # can unfinish course if user unfinish lesson
            course_finished = False

        # update student course progress
        update_body = {
            "$set": {
                "lessons.$[elem].finished": requested_lesson.finished,
                "lessons.$[elem].lesson_completed": requested_lesson.lesson_completed,
                "finished": course_finished,
            },
            "$inc": {"finished_count": finished_count_inc},
        }
        array_filter = [
            {
                "elem.lesson_id": ObjectId(requested_lesson.lesson_id),
                "elem.chapter_id": ObjectId(requested_lesson.chapter_id),
            }
        ]
        response = db_client.course_progress_coll.find_one_and_update(
            filter=update_filter,
            update=update_body,
            array_filters=array_filter,
            return_document=ReturnDocument.AFTER,
        )
        if response == None:
            raise Exception.not_found
    except InvalidId:
        raise Exception.bad_request
    return {"progress": (response["finished_count"] / total_lessons)*100}

# STUDENT CONFIG
def edit_student_config(student_id: str, request: PatchStudentConfigRequestModel) -> UpdateResult:
    try:
        filter = {"type": student_type, "_id": ObjectId(student_id)}

        update_body = {}
        if request.theme != None:
            update_body["theme"] = request.theme
        update = {"$set": update_body}

        result = db_client.user_coll.update_one(filter=filter, update=update)
    
    except InvalidId:
        raise Exception.bad_request
    
    return result

def query_student_config(student_id: str) -> dict:
    try:
        filter = {"_id": ObjectId(student_id), "type": student_type,}
        student = db_client.user_coll.find_one(filter=filter)
        if student != None:
            student["theme"] = str(student["theme"])
        
    except InvalidId:
        raise Exception.bad_request
    
    return student
    