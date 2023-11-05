from pymongo.cursor import Cursor
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId
from .schemas import (
    PatchClassRequestModel,
    PostClassRequestModel,
    PostThreadReplyRequestModel,
    TagModelBody,
    PostThreadRequestModel,
    PatchThreadRequestModel,
)

from ...dependencies import (
    Exception,
    CheckHttpFileType,
    utc_datetime_now,
    timestamp_to_utc_datetime,
    teacher_type,
    student_type,
    class_type,
    course_type,
)


def get_teacher_by_id(teacher_id: str):
    try:
        teacher = db_client.user_coll.find_one(
            {"_id": ObjectId(teacher_id), "type": teacher_type}
        )
        if teacher is None:
            raise Exception.not_found
        teacher["teacher_id"] = str(teacher["_id"])
        teacher["teacher_name"] = teacher["fullname"]
        return teacher
    except InvalidId:
        raise Exception.bad_request


def get_student_by_id(student_id: str):
    try:
        student = db_client.user_coll.find_one(
            {"_id": ObjectId(student_id), "type": student_type}
        )
        if student is None:
            raise Exception.not_found
        student["student_id"] = str(["_id"])
        student["student_name"] = student["fullname"]
        return student
    except InvalidId:
        raise Exception.bad_request


def query_list_tags_by_id(ids: list[str | ObjectId]):
    try:
        object_ids = list(map(ObjectId, ids))

        filter = {"_id": {"$in": object_ids}}
        tags_cursor = db_client.tag_coll.find(filter)
        tags = []
        for tag in tags_cursor:
            tag["tag_id"] = str(tag["_id"])
            tag["tag_name"] = tag["name"]
            tags.append(TagModelBody(**tag))
        return tags

    except InvalidId:
        raise Exception.bad_request


# CLASSES
def query_list_classes(skip: int, limit: int):
    try:
        classes_corsor = db_client.class_coll.find(skip=skip, limit=limit)
    except InvalidId:
        raise Exception.bad_request
    return classes_corsor


def query_class(class_id: str) -> dict | None:
    try:
        class_filter = {"_id": ObjectId(class_id)}
        class_ = db_client.class_coll.find_one(class_filter)
        return class_
    except InvalidId:
        raise Exception.bad_request


def create_class(request: PostClassRequestModel) -> str:
    try:
        # Check valid teacher
        teacher_filter = {"type": teacher_type, "_id": ObjectId(request.teacher_id)}
        teacher_result = db_client.user_coll.find_one(filter=teacher_filter)
        if teacher_result == None:
            raise Exception.unprocessable_content

        # Check valid tag
        for tag_id in request.tag_ids:
            tag_result = db_client.tag_coll.find_one(ObjectId(tag_id))
            if tag_result == None:
                raise Exception.unprocessable_content

        body = {
            "name": request.name,
            "description": request.description,
            "created_date": utc_datetime_now(),
            "class_pic": str(request.class_pic),
            "student_count": 0,
            "max_student": request.max_student,
            "price": request.price,
            "teacher_id": ObjectId(request.teacher_id),
            "class_objective": request.class_objective,
            "class_requirement": request.class_requirement,
            "difficulty_level": request.difficulty_level,
            "tags": [ObjectId(tag_) for tag_ in request.tag_ids],
            "assignment_count": 0,
            "meeting_count": len(request.schedules),
            "schedules": [],
            "open_date": timestamp_to_utc_datetime(request.open_date),
            "registration_ended_date": timestamp_to_utc_datetime(
                request.registration_ended_date
            ),
            "class_ended_date": timestamp_to_utc_datetime(request.class_ended_date),
            "status": "started",
        }

        for sched_ in request.schedules:
            if sched_.start > sched_.end:
                err = Exception.unprocessable_content
                err.__setattr__("detail", "required schedule's start <= end")
            body["schedules"].append(
                {
                    "start": timestamp_to_utc_datetime(sched_.start),
                    "end": timestamp_to_utc_datetime(sched_.end),
                }
            )
        insert_class_result = db_client.class_coll.insert_one(body)
        if insert_class_result.inserted_id == None:
            raise Exception.internal_server_error

        # add class to teacher's owned programs
        push_content = {
            "owned_programs": {
                "type": class_type,
                "program_id": insert_class_result.inserted_id,
            }
        }
        push_result = db_client.user_coll.update_one(
            teacher_filter, {"$push": push_content}
        )
        if push_result.matched_count == 0:
            raise Exception.internal_server_error
        return str(insert_class_result.inserted_id)

    except InvalidId:
        raise Exception.bad_request


def edit_class(class_id: str, request: PatchClassRequestModel):
    try:
        filter = {"_id": ObjectId(class_id)}

        # prepare update body
        set_content = dict()
        push_content = dict()
        pull_content = dict()
        inc_content = dict()
        if request.name != None:
            set_content["name"] = request.name
        if request.class_pic != None:
            set_content["class_pic"] = str(request.class_pic)
        if request.max_student != None:
            # TODO: how to determine if able to change max_student
            set_content["max_student"] = request.max_student
        if request.price != None:
            set_content["price"] = request.price
        if request.description != None:
            set_content["description"] = request.description
        if request.class_requirement != None:
            set_content["class_requirement"] = request.class_requirement
        if request.difficulty_level != None:
            set_content["difficulty_level"] = request.difficulty_level
        if request.open_date != None:
            set_content["open_date"] = timestamp_to_utc_datetime(request.open_date)
        if request.registration_ended_date != None:
            set_content["registration_ended_date"] = timestamp_to_utc_datetime(
                request.registration_ended_date
            )
        if request.class_ended_date != None:
            set_content["class_ended_date"] = timestamp_to_utc_datetime(
                request.class_ended_date
            )

        # class objective
        if request.class_objective != None:
            for objective_ in request.class_objective:
                if objective_.op == "add":
                    if "class_objective" not in push_content:
                        push_content["class_objective"] = {}
                        push_content["class_objective"]["$each"] = []
                    push_content["class_objective"]["$each"].append(objective_.value)
                elif objective_.op == "remove":
                    if "class_objective" not in pull_content:
                        pull_content["class_objective"] = {}
                        pull_content["class_objective"]["$in"] = []
                    pull_content["class_objective"]["$in"].append(objective_.value)

        # tags
        if request.tag != None:
            #  Check duplicate tags
            _class_tag_filter = {
                "_id": ObjectId(class_id),
                "tags": ObjectId(request.tag.tag_id),
            }

            tag_filter = {"_id": ObjectId(request.tag.tag_id)}
            tag = db_client.tag_coll.find_one(tag_filter)
            if tag == None:
                err = Exception.unprocessable_content
                err.__setattr__("detail", "Invalid tag_id")
                raise err

            if request.tag.op == "add":
                _class_tag_check_result = db_client.class_coll.find_one(
                    _class_tag_filter
                )
                if _class_tag_check_result != None:
                    err = Exception.unprocessable_content
                    err.__setattr__("detail", "duplicate class's tag")
                    raise err
                push_content["tags"] = ObjectId(request.tag.tag_id)
            elif request.tag.op == "remove":
                pull_content["tags"] = dict()
                pull_content["tags"]["$in"] = [ObjectId(request.tag.tag_id)]

        # schedules
        if request.schedules != None:
            if request.schedules.op == "add":
                # Check duplicate schedules
                _schedule_filter = {
                    "_id": ObjectId(class_id),
                    "schedules": {
                        "$elemMatch": {
                            "start": timestamp_to_utc_datetime(request.schedules.start),
                            "end": timestamp_to_utc_datetime(request.schedules.end),
                        }
                    },
                }
                _duplicate_check_result = db_client.class_coll.find_one(
                    _schedule_filter
                )
                if _duplicate_check_result != None:
                    err = Exception.unprocessable_content
                    err.__setattr__("detail", "duplicate schedules")
                    raise err
                # check start < end time
                if request.schedules.start > request.schedules.end:
                    err = Exception.unprocessable_content
                    err.__setattr__("detail", "required schedule's start <= end ")
                push_content["schedules"] = {}
                push_content["schedules"]["$each"] = [
                    {
                        "start": timestamp_to_utc_datetime(request.schedules.start),
                        "end": timestamp_to_utc_datetime(request.schedules.end),
                    }
                ]
                if "meeting_count" not in inc_content:
                    inc_content["meeting_count"] = 0
                inc_content["meeting_count"] += 1
            elif request.schedules.op == "remove":
                pull_content["schedules"] = {
                    "$in": [
                        {
                            "start": timestamp_to_utc_datetime(request.schedules.start),
                            "end": timestamp_to_utc_datetime(request.schedules.end),
                        }
                    ]
                }
                if "meeting_count" not in inc_content:
                    inc_content["meeting_count"] = 0
                inc_content["meeting_count"] -= 1

        # mongo doesn't allow multi operation edit
        patch_result = None
        if len(set_content) != 0:
            patch_result = db_client.class_coll.update_one(
                filter, {"$set": set_content}
            )
        if len(push_content) != 0:
            patch_result = db_client.class_coll.update_one(
                filter, {"$push": push_content}
            )
        if len(pull_content) != 0:
            patch_result = db_client.class_coll.update_one(
                filter, {"$pull": pull_content}
            )
        if len(inc_content) != 0:
            patch_result = db_client.class_coll.update_one(
                filter, {"$inc": inc_content}
            )

        if patch_result == None:
            raise Exception.internal_server_error
    except InvalidId:
        raise Exception.bad_request


# STUDENT
def query_list_students_by_class(class_id: str) -> Cursor:
    student_filter = {
        "type": student_type,
        "owned_programs": {
            "$elemMatch": {"type": class_type, "program_id": ObjectId(class_id)}
        },
    }
    students_cur = db_client.user_coll.find(student_filter)
    return students_cur


# THREADS
def query_list_threads(class_id: str, skip: int, limit: int) -> Cursor:
    try:
        filter_ = {"class_id": ObjectId(class_id)}
        thread_cursor = db_client.thread_coll.find(
            filter=filter_, skip=skip, limit=limit
        )
        return thread_cursor
    except InvalidId:
        raise Exception.bad_request


def create_thread(class_id: str, thread_body: PostThreadRequestModel):
    try:
        # check valid class
        valid_class_filter = {"_id": ObjectId(class_id)}
        class_result = db_client.class_coll.find_one(
            filter=valid_class_filter, projection={"teacher_id": 1}
        )
        if class_result == None:
            raise Exception.unprocessable_content

        # insert thread
        thread_to_insert = thread_body.model_dump()
        thread_to_insert["class_id"] = ObjectId(class_id)
        thread_to_insert["teacher_id"] = class_result["teacher_id"]
        thread_to_insert["last_edit"] = utc_datetime_now()
        for i in range(len(thread_to_insert["attachments"])):
            thread_to_insert["attachments"][i]["attachment_type"] = thread_to_insert[
                "attachments"
            ][i]["attachment_type"]

        result = db_client.thread_coll.insert_one(thread_to_insert)
        return str(result.inserted_id)
    except InvalidId:
        raise Exception.bad_request


def query_thread(class_id: str, thread_id: str):
    try:
        filter_ = {"_id": ObjectId(thread_id), "class_id": ObjectId(class_id)}
        thread = db_client.thread_coll.find_one(filter=filter_)
        return thread
    except InvalidId:
        raise Exception.bad_request


def edit_thread(class_id: str, thread_id: str, thread_body: PatchThreadRequestModel):
    try:
        filter_ = {"_id": ObjectId(thread_id), "class_id": ObjectId(class_id)}

        # prepare update body
        set_content = dict()
        push_content = dict()
        pull_content = dict()

        # set update body for each field
        set_content["last_edit"] = utc_datetime_now()
        if thread_body.name != None:
            set_content["name"] = thread_body.name
        if thread_body.text != None:
            set_content["text"] = thread_body.text
        if thread_body.attachments != None:
            for attachment_ in thread_body.attachments:
                if attachment_.op == "add":
                    if "attachments" not in push_content:  # first time add/push
                        push_content["attachments"] = {}
                        push_content["attachments"]["$each"] = []
                    push_content["attachments"]["$each"].append(
                        {
                            "attachment_type": CheckHttpFileType(attachment_.src),
                            "src": attachment_.src,
                        }
                    )
                elif attachment_.op == "remove":
                    if "attachments" not in pull_content:  # first time remove/pull
                        pull_content["attachments"] = {}
                        pull_content["attachments"]["src"] = {}
                        pull_content["attachments"]["src"]["$in"] = []
                    pull_content["attachments"]["src"]["$in"].append(
                        attachment_.src
                    )  # src is id of attachments to delete

        if len(set_content) != 0:
            patch_result = db_client.thread_coll.update_one(
                filter=filter_, update={"$set": set_content}
            )
            if patch_result.matched_count == 0:
                raise Exception.not_found
        if len(push_content) != 0:
            patch_result = db_client.thread_coll.update_one(
                filter=filter_, update={"$push": push_content}
            )
            if patch_result.matched_count == 0:
                raise Exception.not_found
        if len(pull_content) != 0:
            patch_result = db_client.thread_coll.update_one(
                filter=filter_, update={"$pull": pull_content}
            )
            if patch_result.matched_count == 0:
                raise Exception.not_found

        return True
    except InvalidId:
        raise Exception.bad_request


# REPLY
def query_list_thread_replies_by_class(class_id: str) -> Cursor:
    try:
        _filter = {"class_id": ObjectId(class_id)}
        reply_cursor = db_client.thread_reply_coll.find(_filter)
        return reply_cursor
    except InvalidId:
        raise Exception.bad_request


def query_list_thread_replies_by_thread(class_id: str, thread_id: str) -> Cursor:
    try:
        _filter = {"class_id": ObjectId(class_id), "thread_id": ObjectId(thread_id)}
        reply_cursor = db_client.thread_reply_coll.find(_filter)
        return reply_cursor
    except InvalidId:
        raise Exception.bad_request


def create_thread_reply(
    class_id: str, thread_id: str, request: PostThreadReplyRequestModel
) -> ObjectId:
    try:
        body = {
            "class_id": ObjectId(class_id),
            "thread_id": ObjectId(thread_id),
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

        result = db_client.thread_reply_coll.insert_one(body)
        if result.inserted_id == None:
            raise Exception.internal_server_error
        return result.inserted_id
    except InvalidId:
        raise Exception.bad_request
