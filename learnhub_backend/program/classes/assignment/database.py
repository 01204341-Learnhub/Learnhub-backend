from pymongo.results import UpdateResult
from datetime import datetime, timedelta, timezone
from ..database import db_client
from bson.objectid import ObjectId
from bson.errors import InvalidId

from ....dependencies import Exception, CheckHttpFileType

from .schemas import (
    PatchAssignmentRequestModel,
)


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
                            "src": str(patch_body["attachments"][i]["src"]),
                            "attachment_type": CheckHttpFileType(
                                str(patch_body["attachments"][i]["src"])
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
