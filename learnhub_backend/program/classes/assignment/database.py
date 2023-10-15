from pymongo.cursor import Cursor
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ....dependencies import (
    Exception,
    student_type,
    teacher_type,
    class_type,
    course_type,
    utc_datetime_now,
    timestamp_to_utc_datetime,
)

from .schemas import (
    PatchAssignmentRequestModel,
    PostAssignmentReplyRequestModel,
    PostClassAssignmentRequestModel,
    PutAssignmentSubmitRequestModel,
)

from .config import (
    AssignmentStatus,
    SubmissionStatus,
)


# STUDENT
def query_student_profile(student_id: str) -> dict:
    try:
        filter = {"_id": ObjectId(student_id), "type": student_type}
        student = db_client.user_coll.find_one(filter)
        if student == None:
            raise Exception.not_found
        student_res = {
            "student_id": student_id,
            "student_name": student["fullname"],
        }
        if "profile_pic" not in student:
            student_res["profile_pic"] = None
        else:
            student_res["profile_pic"] = student["profile_pic"]

        return student_res
    except InvalidId:
        raise Exception.bad_request


# ASSIGNMENTS
def query_assignments_by_class_id(class_id: str) -> Cursor:
    try:
        filter = {"class_id": ObjectId(class_id)}
        assignments_cur = db_client.assignment_coll.find(filter)
        return assignments_cur
    except InvalidId:
        raise Exception.bad_request


def query_single_assignment(class_id: str, assignment_id: str) -> dict | None:
    try:
        filter = {"_id": ObjectId(assignment_id), "class_id": ObjectId(class_id)}
        assignment = db_client.assignment_coll.find_one(filter)
        return assignment
    except InvalidId:
        raise Exception.bad_request


def create_assignment(class_id: str, request: PostClassAssignmentRequestModel) -> str:
    try:
        # check valid class
        class_filter = {"_id": ObjectId(class_id)}
        class_ = db_client.class_coll.find_one(class_filter)
        if class_ == None:
            raise Exception.not_found

        body = {
            "class_id": ObjectId(class_id),
            "name": request.name,
            "created_date": utc_datetime_now(),
            "group_name": request.group_name,
            "max_score": request.max_score,
            "text": request.text,
            "attachments": [
                {"attachment_type": at_.attachment_type, "src": at_.src}
                for at_ in request.attachments
            ],
            "last_edit": utc_datetime_now(),
            "status": AssignmentStatus.open,
            "due_date": timestamp_to_utc_datetime(request.due_date),
        }
        response = db_client.assignment_coll.insert_one(body)
        if response.inserted_id == None:
            raise Exception.internal_server_error

        # update class assignment_count
        inc_content = {"assignment_count": 1}
        update_res = db_client.class_coll.update_one(
            class_filter, {"$inc": inc_content}
        )
        if update_res.matched_count == 0:
            raise Exception.internal_server_error

        _create_class_students_submission(class_id, str(response.inserted_id))
        return str(response.inserted_id)
    except InvalidId:
        raise Exception.bad_request


def _create_class_students_submission(class_id: str, assignment_id: str):
    # Create all class's student submissions
    body_template = {
        "assignment_id": ObjectId(assignment_id),
        "class_id": ObjectId(class_id),
        "status": SubmissionStatus.unsubmit,
        "score": 0,
        "submission_date": timestamp_to_utc_datetime(0),
        "attachments": [],
    }
    bodies = []

    student_filter = {
        "type": student_type,
        "owned_programs.program_id": ObjectId(class_id),
        "owned_programs.type": "class",
    }
    students_cur = db_client.user_coll.find(student_filter)
    for stu_ in students_cur:
        body = body_template
        body["student_id"] = ObjectId(stu_["_id"])
        bodies.append(body)
    if len(bodies) == 0:
        return
    _ = db_client.assignment_submission_coll.insert_many(bodies)


def edit_assignment(
    class_id: str, assignment_id: str, patch_body_: PatchAssignmentRequestModel
):
    try:
        patch_body = patch_body_.model_dump()  # info to update
        filter = {"_id": ObjectId(assignment_id), "class_id": ObjectId(class_id)}

        # prepare update body
        update_body_add = {"$push": {"attachments": {"$each": []}}}

        update_body_delete = {
            "$pull": {
                "attachments": {"src": {"$in": []}}
            },  # src is id of attachments to delete
        }

        update_body_edit = {
            "$set": {},
        }
        array_filter = []

        # set update body for each field
        update_body_edit["$set"]["last_edit"] = utc_datetime_now()
        if patch_body["name"] is not None:
            update_body_edit["$set"]["name"] = patch_body["name"]
        if patch_body["group_name"] is not None:
            update_body_edit["$set"]["group_name"] = patch_body["group_name"]
        # if patch_body["max_score"] is not None:
        #     update_body_edit["$set"]["max_score"] = patch_body["max_score"]
        if patch_body["due_date"] is not None:
            update_body_edit["$set"]["due_date"] = timestamp_to_utc_datetime(
                patch_body["due_date"]
            )
        if patch_body["status"] is not None:
            update_body_edit["$set"]["status"] = patch_body[
                "status"
            ]  # TODO:make status do something
        if patch_body["text"] is not None:
            update_body_edit["$set"]["text"] = patch_body["text"]
        if patch_body["attachments"] is not None:
            for i in range(len(patch_body["attachments"])):
                # set array filter and update body for each operation on attachments

                if patch_body["attachments"][i]["op"] == "add":
                    update_body_add["$push"]["attachments"]["$each"].append(
                        # document to add to array
                        {
                            "src": str(patch_body["attachments"][i]["src"]),
                            "attachment_type": str(
                                patch_body["attachments"][i]["attachment_type"]
                            ),
                        }
                    )

                elif patch_body["attachments"][i]["op"] == "remove":
                    update_body_delete["$pull"]["attachments"]["src"]["$in"].append(
                        # id of document to delete from array
                        str(patch_body["attachments"][i]["src"])
                    )
                else:
                    raise Exception.unprocessable_content

        # update each operation
        result = db_client.assignment_coll.update_one(
            filter=filter, update=update_body_add
        )
        if result.matched_count == 0:
            raise Exception.not_found
        result = db_client.assignment_coll.update_one(
            filter=filter, update=update_body_delete
        )
        if result.matched_count == 0:
            raise Exception.not_found
        result = db_client.assignment_coll.update_one(
            filter=filter, update=update_body_edit, array_filters=array_filter
        )
        if result.matched_count == 0:
            raise Exception.not_found
        return True
    except InvalidId:
        raise Exception.bad_request


# SUBMISSION
def query_list_submission_by_assignment_id(class_id: str, assignment_id: str) -> Cursor:
    filter = {
        "class_id": ObjectId(class_id),
        "assignment_id": ObjectId(assignment_id),
    }

    subs_cur = db_client.assignment_submission_coll.find(filter)
    return subs_cur


def query_single_submission_by_student_id(
    class_id: str, assignment_id: str, student_id: str
) -> dict | None:
    filter = {
        "student_id": ObjectId(student_id),
        "class_id": ObjectId(class_id),
        "assignment_id": ObjectId(assignment_id),
    }

    submission = db_client.assignment_submission_coll.find_one(filter)
    return submission


def score_submission(class_id: str, assignment_id: str, student_id: str, score: float):
    filter = {
        "student_id": ObjectId(student_id),
        "class_id": ObjectId(class_id),
        "assignment_id": ObjectId(assignment_id),
    }

    # Check if submission status is not unsubmit
    subm = db_client.assignment_submission_coll.find_one(filter)
    if subm == None:
        raise Exception.not_found
    if subm["status"] == SubmissionStatus.unsubmit:
        err = Exception.unprocessable_content
        err.__setattr__("detail", "Submission not yet submit")
        raise err
    set_content = {"score": score}
    result = db_client.assignment_submission_coll.update_one(
        filter, {"$set": set_content}
    )
    if result.matched_count == 0:
        raise Exception.not_found


def update_submission(
    class_id: str,
    assignment_id: str,
    student_id: str,
    request: PutAssignmentSubmitRequestModel,
) -> str:
    try:
        filter = {
            "student_id": ObjectId(student_id),
            "assignment_id": ObjectId(assignment_id),
            "class_id": ObjectId(class_id),
        }

        # check assignment status first
        submission = db_client.assignment_submission_coll.find_one(filter)
        if submission == None:
            raise Exception.not_found
        if submission["status"] != SubmissionStatus.unsubmit:
            err = Exception.unprocessable_content
            err.__setattr__("detail", "Required submission unsubmit")
            raise err

        set_content = dict()
        set_content["student_id"] = ObjectId(student_id)
        set_content["assignment_id"] = ObjectId(assignment_id)
        set_content["class_id"] = ObjectId(class_id)
        set_content["status"] = SubmissionStatus.uncheck
        set_content["score"] = 0
        set_content["submission_date"] = utc_datetime_now()
        set_content["attachments"] = [
            {"attachment_type": at_.attachment_type, "src": at_.src}
            for at_ in request.attachments
        ]

        result = db_client.assignment_submission_coll.find_one_and_update(
            filter, {"$set": set_content}
        )
        if result == None:
            raise Exception.internal_server_error

        return str(result["student_id"])

    except InvalidId:
        raise Exception.bad_request


def unsubmit_submission(class_id: str, assignment_id: str, student_id: str):
    try:
        filter = {
            "student_id": ObjectId(student_id),
            "assignment_id": ObjectId(assignment_id),
            "class_id": ObjectId(class_id),
        }
        set_content = dict()
        set_content["status"] = SubmissionStatus.unsubmit
        set_content["score"] = 0

        result = db_client.assignment_submission_coll.update_one(
            filter, {"$set": set_content}
        )
        if result.matched_count == 0:
            raise Exception.not_found
    except InvalidId:
        raise Exception.bad_request


# REPLY
def query_list_assingment_replies_by_class(class_id: str) -> Cursor:
    try:
        _filter = {"class_id": ObjectId(class_id)}
        reply_cursor = db_client.assignment_reply_coll.find(_filter)
        return reply_cursor
    except InvalidId:
        raise Exception.bad_request


def query_list_assignment_replies_by_assignment(
    class_id: str, assignment_id: str
) -> Cursor:
    try:
        _filter = {
            "class_id": ObjectId(class_id),
            "assignment_id": ObjectId(assignment_id),
        }
        reply_cursor = db_client.assignment_reply_coll.find(_filter)
        return reply_cursor
    except InvalidId:
        raise Exception.bad_request


def create_assingment_reply(
    class_id: str, assignment_id: str, request: PostAssignmentReplyRequestModel
) -> ObjectId:
    try:
        body = {
            "class_id": ObjectId(class_id),
            "assignment_id": ObjectId(assignment_id),
            "user": {
                "user_id": ObjectId(request.user_id),
                "user_type": request.user_type,
            },
            "text": request.text,
            "reply_date": utc_datetime_now(),
        }
        # validate user_id
        if request.user_type == student_type:
            _student_filter = {"_id": ObjectId(request.user_id), "type": student_type}
            _student = db_client.user_coll.find_one(_student_filter)
            if _student == None:
                err = Exception.not_found
                err.__setattr__("detail", "student not found")
                raise err
        elif request.user_type == teacher_type:
            _teacher_filter = {"_id": ObjectId(request.user_id), "type": teacher_type}
            _teacher = db_client.user_coll.find_one(_teacher_filter)
            if _teacher == None:
                err = Exception.not_found
                err.__setattr__("detail", "teacher not found")
                raise err

        result = db_client.assignment_reply_coll.insert_one(body)
        if result.inserted_id == None:
            raise Exception.internal_server_error
        return result.inserted_id
    except InvalidId:
        raise Exception.bad_request
