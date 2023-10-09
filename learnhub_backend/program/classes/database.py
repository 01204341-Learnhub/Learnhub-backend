from pymongo.cursor import Cursor
from pymongo.results import UpdateResult
from datetime import datetime, timedelta, timezone
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId
from .schemas import (
    PatchClassRequestModel,
    PostClassRequestModel,
    TagModelBody,
    PostThreadRequestModel,
)

from ...dependencies import Exception, CheckHttpFileType


def get_teacher_by_id(teacher_id: str):
    try:
        teacher = db_client.user_coll.find_one({"_id": ObjectId(teacher_id)})
        if teacher is None:
            raise Exception.not_found
        teacher["teacher_id"] = str(teacher["_id"])
        teacher["teacher_name"] = teacher["fullname"]
        return teacher
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
        body = {
            "name": request.name,
            "description": request.description,
            "created_date": datetime.now(tz=timezone(timedelta(hours=7))),
            "class_pic": str(request.class_pic),
            "student_count": 0,
            "max_student": request.max_student,
            "rating": 0,
            "review_count": 0,
            "price": request.price,
            "teacher_id": ObjectId(request.teacher_id),
            "class_objective": request.class_objective,
            "class_requirement": request.class_requirement,
            "difficulty_level": request.difficulty_level,
            "tags": [ObjectId(tag_) for tag_ in request.tag_ids],
            "assignment_count": 0,
            "meeting_count": len(request.schedules),
            "chapter_count": 0,
            "schedules": [],
            "open_date": datetime.fromtimestamp(request.open_date),
            "registration_ended_date": datetime.fromtimestamp(
                request.registration_ended_date
            ),
            "class_ended_date": datetime.fromtimestamp(request.class_ended_date),
            "status": "started",
        }

        for sched_ in request.schedules:
            if sched_.start > sched_.end:
                err = Exception.unprocessable_content
                err.__setattr__("detail", "required schedule's start <= end")
            body["schedules"].append(
                {
                    "start": datetime.fromtimestamp(sched_.start),
                    "end": datetime.fromtimestamp(sched_.end),
                }
            )
        result = db_client.class_coll.insert_one(body)
        if result.inserted_id == None:
            raise Exception.internal_server_error
        else:
            return str(result.inserted_id)
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
            set_content["open_date"] = datetime.fromtimestamp(request.open_date)
        if request.registration_ended_date != None:
            set_content["registration_ended_date"] = datetime.fromtimestamp(
                request.registration_ended_date
            )
        if request.class_ended_date != None:
            set_content["class_ended_date"] = datetime.fromtimestamp(
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
            _class_tag_check_result = db_client.class_coll.find_one(_class_tag_filter)
            if _class_tag_check_result != None:
                err = Exception.unprocessable_content
                err.__setattr__("detail", "duplicate class's tag")
                raise err

            tag_filter = {"_id": ObjectId(request.tag.tag_id)}
            tag = db_client.tag_coll.find_one(tag_filter)
            if tag == None:
                err = Exception.unprocessable_content
                err.__setattr__("detail", "Invalid tag_id")
                raise err

            if request.tag.op == "add":
                push_content["tags"] = ObjectId(request.tag.tag_id)
            elif request.tag.op == "remove":
                pull_content["tags"]["$in"] = [ObjectId(request.tag.tag_id)]

        # schedules
        if request.schedules != None:
            if request.schedules.op == "add":
                # Check duplicate schedules
                _schedule_filter = {
                    "_id": ObjectId(class_id),
                    "schedules": {
                        "$elemMatch": {
                            "start": datetime.fromtimestamp(request.schedules.start),
                            "end": datetime.fromtimestamp(request.schedules.end),
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
                        "start": datetime.fromtimestamp(request.schedules.start),
                        "end": datetime.fromtimestamp(request.schedules.end),
                    }
                ]
                if "meeting_count" not in inc_content:
                    inc_content["meeting_count"] = 0
                inc_content["meeting_count"] += 1
            elif request.schedules.op == "remove":
                pull_content["schedules"] = {
                    "$in": [
                        {
                            "start": datetime.fromtimestamp(request.schedules.start),
                            "end": datetime.fromtimestamp(request.schedules.end),
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
        thread_to_insert["last_edit"] = datetime.now(
            tz=timezone(timedelta(hours=7))
        )  # bangkok time
        for i in range(len(thread_to_insert["attachments"])):
            thread_to_insert["attachments"][i]["attachment_type"] = CheckHttpFileType(
                thread_to_insert["attachments"][i]["src"]
            )

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
