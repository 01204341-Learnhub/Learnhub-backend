from logging import error
from pymongo.results import DeleteResult, UpdateResult
from pymongo import ReturnDocument
from bson.objectid import ObjectId
from bson.errors import InvalidId

from .schemas import (
    PatchStudentPaymentMethodRequestModel,
    PostStudentBasketItemRequestModel,
    PostStudentPaymentMethodRequestModel,
    PostStudentRequestModel,
    PatchStudentRequestModel,
    LessonProgressModelBody,
    GetStudentConfigResponseModel,
    PatchStudentConfigRequestModel,
)
from ..database import db_client


from ..dependencies import (
    student_type,
    teacher_type,
    course_type,
    Exception,
)


def query_teacher_profile(teacher_id: str) -> dict:
    filter = {"_id": ObjectId(teacher_id), "type": teacher_type}
    teacher = db_client.user_coll.find_one(filter)
    if teacher == None:
        raise Exception.internal_server_error

    teacher_res = {
        "teacher_id": teacher_id,
        "teacher_name": teacher["fullname"],
        "profile_pic": teacher["profile_pic"],
    }
    return teacher_res


# PROGRAM
def query_course(course_id: str):
    filter = {"_id": ObjectId(course_id)}
    course = db_client.course_coll.find_one(filter)
    if course == None:
        raise Exception.not_found
    return course


def query_class(class_id: str):
    filter = {"_id": ObjectId(class_id)}
    cls = db_client.class_coll.find_one(filter)
    if cls == None:
        raise Exception.not_found
    return cls


def query_multiple_classes(class_ids: list[str]):
    filter = {"_id": {"$in": [ObjectId(id_) for id_ in class_ids]}}
    classes_cur = db_client.class_coll.find(filter)
    return classes_cur


# STUDENT
def query_list_students(skip: int = 0, limit: int = 100) -> list:
    try:
        filter = {"type": student_type}
        students_cursor = db_client.user_coll.find(
            skip=skip, limit=limit, filter=filter
        )
        students = []
        for student in students_cursor:
            student["student_id"] = str(student["_id"])
            students.append(student)

        return students
    except InvalidId:
        raise Exception.bad_request


def query_student(student_id: str) -> dict:
    try:
        filter = {"_id": ObjectId(student_id), "type": student_type}
        student = db_client.user_coll.find_one(filter=filter)
        if student == None:
            raise Exception.not_found
        student["student_id"] = str(student["_id"])
        return student
    except InvalidId:
        raise Exception.bad_request


def create_student(request: PostStudentRequestModel):
    try:
        student_body = dict()
        student_body["uid"] = request.uid
        student_body["username"] = request.username
        student_body["email"] = request.email
        student_body["fullname"] = request.fullname
        if request.profile_pic != None:
            student_body["profile_pic"] = str(request.profile_pic)
        student_body["config"] = {"theme": "light"}
        student_body["type"] = "student"
        student_body["wishlist"] = []
        student_body["basket"] = []
        student_body["interested_tags"] = []
        student_body["owned_programs"] = []
        student_body["payment_methods"] = []

        # Check duplicate uid
        uid_filter = {"type": student_type, "uid": request.uid}
        check_uid = db_client.user_coll.find_one(uid_filter)
        if check_uid != None:
            error_uid = Exception.unprocessable_content
            error_uid.__setattr__("detail", "UID duplicate")
            raise error_uid

        # Check duplicate email
        email_filter = {"type": student_type, "email": request.email}
        check_email = db_client.user_coll.find_one(email_filter)
        if check_email != None:
            error_email = Exception.unprocessable_content
            error_email.__setattr__("detail", "Email Duplicate")
            raise error_email

        # Add student
        result = db_client.user_coll.insert_one(student_body)
        return str(result.inserted_id)
    except InvalidId:
        raise Exception.bad_request


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


# STUDENT COURSE PROGRESS
def query_student_course_progress(student_id: str, course_id: str) -> dict:
    try:
        # find student course progress
        filter = {"student_id": ObjectId(student_id), "course_id": ObjectId(course_id)}
        student_course_progress = db_client.course_progress_coll.find_one(filter=filter)

        if student_course_progress == None:
            raise Exception.not_found
        return student_course_progress
    except InvalidId:
        raise Exception.bad_request


def edit_student_course_progress(
    student_id: str, course_id: str, requested_lesson: LessonProgressModelBody
):
    try:
        # find total lessons in course
        total_lessons_filter = {"_id": ObjectId(course_id)}
        total_lessons_projection = {"video_count": 1, "quiz_count": 1, "file_count": 1}
        total_lessons_res = db_client.course_coll.find_one(
            filter=total_lessons_filter, projection=total_lessons_projection
        )
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
        check_res = db_client.course_progress_coll.find_one(filter=update_filter)
        if check_res == None:
            raise Exception.not_found
        les_finished_already = False
        for lesson in check_res["lessons"]:
            if lesson["lesson_id"] == ObjectId(requested_lesson.lesson_id) and lesson[
                "chapter_id"
            ] == ObjectId(requested_lesson.chapter_id):
                if lesson["finished"] == True:
                    les_finished_already = True
                    break

        # only increment finished_count if lesson is finished (in request) and not finished already(in DB)
        if requested_lesson.finished == True and les_finished_already == False:
            finished_count_inc = 1
        elif (
            requested_lesson.finished == False and les_finished_already == True
        ):  # decrement finished_count if user unfinish lesson
            finished_count_inc = -1
        else:
            finished_count_inc = 0

        # check if course is finished after updating
        if check_res["finished_count"] + finished_count_inc == total_lessons:
            course_finished = True
        else:  # can unfinish course if user unfinish lesson
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
    return {"progress": (response["finished_count"] / total_lessons) * 100}


# STUDENT CONFIG
def query_student_config(student_id: str) -> dict:
    try:
        filter = {
            "_id": ObjectId(student_id),
            "type": student_type,
        }
        student = db_client.user_coll.find_one(filter=filter)
        if student == None:
            raise Exception.not_found
        return student

    except InvalidId:
        raise Exception.bad_request


def edit_student_config(
    student_id: str, request: PatchStudentConfigRequestModel
) -> UpdateResult:
    try:
        filter = {"type": student_type, "_id": ObjectId(student_id)}

        update_body = {}
        if request.theme != None:
            update_body["config"] = {}
            update_body["config"]["theme"] = request.theme
        update = {"$set": update_body}

        result = db_client.user_coll.update_one(filter=filter, update=update)
        return result

    except InvalidId:
        raise Exception.bad_request


# PAYMENT METHOD
def create_student_payment_method(
    student_id: str, request: PostStudentPaymentMethodRequestModel
) -> str:
    try:
        filter = {"type": student_type, "_id": ObjectId(student_id)}

        payment_body = dict()
        oid = ObjectId()
        update_body = {"$push": {"payment_methods": payment_body}}
        payment_body["payment_method_id"] = oid
        payment_body["name"] = request.name
        payment_body["type"] = request.type
        payment_body["card_number"] = request.card_number
        payment_body["cvc"] = request.cvc
        payment_body["expiration_date"] = request.expiration_date
        payment_body["holder_fullname"] = request.holder_fullname

        result = db_client.user_coll.update_one(filter, update_body)
        if result.matched_count == 0:
            raise Exception.not_found

        return str(oid)

    except InvalidId:
        raise Exception.bad_request


def edit_student_payment_method(
    student_id: str,
    payment_method_id: str,
    request: PatchStudentPaymentMethodRequestModel,
):
    try:
        array_filter = {
            "x.payment_method_id": ObjectId(payment_method_id),
        }

        filter = {
            "type": student_type,
            "_id": ObjectId(student_id),
        }

        payment_body = {}
        patch_body = {"$set": payment_body}
        if request.name != None:
            payment_body["payment_methods.$[x].name"] = request.name
        if request.type != None:
            payment_body["payment_methods.$[x].type"] = request.type
        if request.card_number != None:
            payment_body["payment_methods.$[x].card_number"] = request.card_number
        if request.cvc != None:
            payment_body["payment_methods.$[x].cvc"] = request.cvc
        if request.expiration_date != None:
            payment_body[
                "payment_methods.$[x].expiration_date"
            ] = request.expiration_date
        if request.holder_fullname != None:
            payment_body[
                "payment_methods.$[x].holder_fullname"
            ] = request.holder_fullname

        result = db_client.user_coll.update_one(
            filter, patch_body, array_filters=[array_filter]
        )
        if result.matched_count == 0:
            raise Exception.not_found
    except InvalidId:
        raise Exception.bad_request


def remove_student_payment_method(student_id: str, payment_method_id: str):
    try:
        filter = {
            "type": student_type,
            "_id": ObjectId(student_id),
        }

        update = {
            "$pull": {
                "payment_methods": {"payment_method_id": ObjectId(payment_method_id)}
            }
        }

        result = db_client.user_coll.update_one(filter, update)
        if result.matched_count == 0:
            raise Exception.not_found

    except InvalidId:
        raise Exception.bad_request


# BASKET
def query_student_basket(student_id: str):
    try:
        student_filter = {
            "type": student_type,
            "_id": ObjectId(student_id),
        }
        student = db_client.user_coll.find_one(student_filter)
        if student == None:
            raise Exception.not_found

        basket = student["basket"]

        for i, item in enumerate(basket):
            basket[i]["basket_item_id"] = str(item["basket_item_id"])
            basket[i]["program_id"] = str(item["program_id"])
        return basket

    except InvalidId:
        raise Exception.bad_request


def create_student_basket_item(
    student_id: str, request: PostStudentBasketItemRequestModel
) -> str:
    try:
        # Check for duplicate owned_course
        own_course_filter = {
            "type": student_type,
            "_id": ObjectId(student_id),
            "owned_programs.program_id": ObjectId(request.program_id),
        }
        own_course = db_client.user_coll.find_one(own_course_filter)
        if own_course != None:
            e = Exception.unprocessable_content
            e.__setattr__("detail", "Program already owned")
            raise e

        # Check for duplicate basket_item
        basket_filter = {
            "type": student_type,
            "_id": ObjectId(student_id),
            "basket.program_id": ObjectId(request.program_id),
        }
        basket_result = db_client.user_coll.find_one(basket_filter)
        if basket_result != None:
            e = Exception.unprocessable_content
            e.__setattr__("detail", "Program already in basket")
            raise e

        # Check for valid program
        program_filter = {"_id": ObjectId(request.program_id)}
        if request.type == "course":
            program_result = db_client.course_coll.find_one(program_filter)
        elif request.type == "class":
            program_result = db_client.class_coll.find_one(program_filter)
        else:
            err = Exception.unprocessable_content
            err.__setattr__("detail", "Invalid type")
            raise err
        if program_result == None:
            err = Exception.unprocessable_content
            err.__setattr__("detail", "Invalid Program_id, Program does not exists")
            raise err

        # update basket
        basket_item = dict()
        update = {"$push": {"basket": basket_item}}

        basket_item_id = ObjectId()
        basket_item["basket_item_id"] = basket_item_id
        basket_item["program_id"] = ObjectId(request.program_id)
        basket_item["type"] = request.type

        student_filter = {"type": student_type, "_id": ObjectId(student_id)}
        result = db_client.user_coll.update_one(student_filter, update)
        if result.matched_count == 0:
            raise Exception.not_found
        return str(basket_item_id)
    except InvalidId:
        raise Exception.bad_request


def remove_student_basket_item(student_id: str, basket_item_id: str):
    try:
        student_filter = {
            "type": student_type,
            "_id": ObjectId(student_id),
        }
        update = {"$pull": {"basket": {"basket_item_id": ObjectId(basket_item_id)}}}
        result = db_client.user_coll.update_one(student_filter, update)
        if result.matched_count == 0:
            raise Exception.not_found

    except InvalidId:
        raise Exception.bad_request
