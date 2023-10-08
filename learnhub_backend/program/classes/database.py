from pymongo.results import UpdateResult
from datetime import datetime, timedelta, timezone
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId
from .schemas import (
    TagModelBody,
    PatchAssignmentRequestModel,
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


# ASSIGNMENTS
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
        update_body_edit["$set"]["last_edit"] = datetime.now(
            tz=timezone(timedelta(hours=7))
        )  # bangkok time
        if patch_body["name"] is not None:
            update_body_edit["$set"]["name"] = patch_body["name"]
        if patch_body["group_name"] is not None:
            update_body_edit["$set"]["group_name"] = patch_body["group_name"]
        if patch_body["max_score"] is not None:
            update_body_edit["$set"]["max_score"] = patch_body["max_score"]
        if patch_body["due_time"] is not None:
            update_body_edit["$set"]["due_time"] = datetime.fromtimestamp(
                patch_body["due_time"]
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
                            "src": str(patch_body["attachments"][i]["new_src"]),
                            "attachment_type": CheckHttpFileType(
                                str(patch_body["attachments"][i]["new_src"])
                            ),
                        }
                    )

                elif patch_body["attachments"][i]["op"] == "delete":
                    update_body_delete["$pull"]["attachments"]["src"]["$in"].append(
                        # id of document to delete from array
                        str(patch_body["attachments"][i]["old_src"])
                    )

                elif patch_body["attachments"][i]["op"] == "edit":
                    array_filter.append(
                        # filter to find document to update in array
                        {f"elem{i}.src": str(patch_body["attachments"][i]["old_src"])}
                    )
                    # update body for document to update in array
                    update_body_edit["$set"][f"attachments.$[elem{i}].src"] = str(
                        patch_body["attachments"][i]["new_src"]
                    )

                    update_body_edit["$set"][
                        f"attachments.$[elem{i}].attachment_type"
                    ] = str(
                        CheckHttpFileType(str(patch_body["attachments"][i]["new_src"]))
                    )

                else:
                    raise Exception.unprocessable_content

        # update each operation
        # TODO: change to assignment_coll
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
