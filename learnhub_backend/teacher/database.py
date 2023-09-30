from bson.objectid import ObjectId
from bson.errors import InvalidId

from .schemas import (
    PatchTeacherRequestModel,
    PostTeacherRequestModel,
)
from ..database import (
    db_client,
)
from ..dependencies import (
    teacher_type,
    Exception,
)


# TEACHERS
def query_list_teachers(skip: int = 0, limit: int = 100) -> list:
    filter = {"type": teacher_type}
    teachers_cursor = db_client.user_coll.find(skip=skip, limit=limit, filter=filter)
    teachers = []
    for teacher in teachers_cursor:
        teacher["teacher_id"] = str(teacher["_id"])
        teachers.append(teacher)

    return teachers


def create_teacher(request: PostTeacherRequestModel):
    try:
        teacher_body = dict()
        teacher_body["uid"] = request.uid
        teacher_body["username"] = request.username
        teacher_body["email"] = request.email
        teacher_body["fullname"] = request.fullname
        if request.profile_pic != None:
            teacher_body["profile_pic"] = str(request.profile_pic)
        teacher_body["config"] = {"theme": "light"}
        teacher_body["type"] = teacher_type
        teacher_body["owned_programs"] = []

        # Check duplicate uid
        uid_filter = {"type": teacher_type, "uid": request.uid}
        check_uid = db_client.user_coll.find_one(uid_filter)
        if check_uid != None:
            error_uid = Exception.unprocessable_content
            error_uid.__setattr__("detail", "UID duplicate")
            raise error_uid

        # Check duplicate email
        email_filter = {"type": teacher_type, "email": request.email}
        check_email = db_client.user_coll.find_one(email_filter)
        if check_email != None:
            error_email = Exception.unprocessable_content
            error_email.__setattr__("detail", "Email Duplicate")
            raise error_email

        # Add teacher
        result = db_client.user_coll.insert_one(teacher_body)
        return str(result.inserted_id)
    except InvalidId:
        raise Exception.bad_request


def query_teacher(teacher_id: str):
    try:
        filter = {"type": teacher_type, "_id": ObjectId(teacher_id)}
        teacher = db_client.user_coll.find_one(filter)
        if teacher == None:
            raise Exception.not_found
        teacher["teacher_id"] = str(teacher["_id"])
        return teacher

    except InvalidId:
        raise Exception.bad_request


def edit_teacher(teacher_id: str, request: PatchTeacherRequestModel):
    try:
        filter = {"type": teacher_type, "_id": ObjectId(teacher_id)}
        patch_content = {}
        patch_body = {"$set": patch_content}
        if request.username != None:
            patch_content["username"] = request.username
        if request.fullname != None:
            patch_content["fullname"] = request.fullname
        if request.profile_pic != None:
            patch_content["profile_pic"] = str(request.profile_pic)

        update_result = db_client.user_coll.update_one(filter, patch_body)
        if update_result.matched_count == 0:
            raise Exception.not_found
        return

    except InvalidId:
        raise Exception.bad_request
