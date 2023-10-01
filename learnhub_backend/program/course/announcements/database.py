from datetime import datetime, timedelta, timezone
from bson.objectid import ObjectId
from bson.errors import InvalidId
import pprint

from .schemas import (
    PostCourseAnnouncementRequestModel,
    PatchCourseAnnouncementRequestModel,
)
from learnhub_backend.database import db_client
from learnhub_backend.dependencies import (
    Exception,
    CheckHttpFileType,
)
#TODO: optional add this to dependencies
def get_teacher_by_id(teacher_id: str):
    try:
        teacher = db_client.user_coll.find_one({"_id": ObjectId(teacher_id)})
        if teacher is None:
            raise Exception.not_found
        teacher["teacher_id"] = str(teacher["_id"])
        teacher["teacher_name"] = teacher["fullname"]
        pprint.pprint(teacher)
        return teacher
    except InvalidId:
        raise Exception.bad_request

def list_course_announcement(course_id: str, skip: int = 0, limit: int = 100):
    try:
        q = {"course_id": ObjectId(course_id)}

        announcements_cursor = db_client.annoucement_coll.find(
            q, skip=skip, limit=limit
        )
        announcements = []
        for announcement in announcements_cursor:
            announcement["announcement_id"] = str(announcement["_id"])
            announcement["last_edit"] = int(
                datetime.timestamp(announcement["last_edit"])
            )
            announcements.append(announcement)
    except InvalidId:
        raise Exception.bad_request
    return announcements


def create_course_announcement(
    course_id: str, announcement_body: PostCourseAnnouncementRequestModel
) -> str:
    # Check for valid course
    valid_course_filter = {"_id": ObjectId(course_id)}
    course_result = db_client.course_coll.find_one(filter=valid_course_filter)
    if course_result == None:
        raise Exception.unprocessable_content

    # Insert new announcement
    announcement_body_to_inserted = announcement_body.model_dump()
    announcement_body_to_inserted["course_id"] = ObjectId(course_id)
    announcement_body_to_inserted["teacher_id"] = course_result["teacher_id"]
    announcement_body_to_inserted["last_edit"] = datetime.now(
        tz=timezone(timedelta(hours=7))
    )  # bangkok time
    for i in range(len(announcement_body_to_inserted["attachments"])):
        announcement_body_to_inserted["attachments"][i]["src"] = str(
            announcement_body_to_inserted["attachments"][i]["src"]
        )
        announcement_body_to_inserted["attachments"][i][
            "attachment_type"
        ] = CheckHttpFileType(announcement_body_to_inserted["attachments"][i]["src"])
    response = db_client.annoucement_coll.insert_one(announcement_body_to_inserted)
    created_id = response.inserted_id
    return str(created_id)


def query_course_announcement(course_id: str, announcement_id: str) -> dict:
    try:
        filter = {"_id": ObjectId(announcement_id), "course_id": ObjectId(course_id)}
        announcement = db_client.annoucement_coll.find_one(filter=filter)
        if announcement is None:
            raise Exception.not_found
        return announcement
    except InvalidId:
        raise Exception.bad_request


def edit_course_announcement(
    course_id: str,
    announcement_id: str,
    request_body: PatchCourseAnnouncementRequestModel,
):
    try:
        announcement_body = request_body.model_dump() # info to update
        filter = {"_id": ObjectId(announcement_id), "course_id": ObjectId(course_id)}
        
        # prepare update body
        update_body_add = {"$push": {"attachments": {"$each": []}}}

        update_body_delete = {
            "$pull": {"attachments": {"src": {"$in": []}}}, # src is id of attachments to delete
        }
        
        update_body_edit = {
            "$set": {},
        }
        array_filter = []

        # set update body for each field
        if announcement_body["name"] is not None:
            update_body_edit["$set"]["name"] = announcement_body["name"]
        if announcement_body["text"] is not None:
            update_body_edit["$set"]["text"] = announcement_body["text"]
        if announcement_body["attachments"] is not None:
            for i in range(len(announcement_body["attachments"])):
                # set array filter and update body for each operation on attachments

                if announcement_body["attachments"][i]["op"] == "add":
                    update_body_add["$push"]["attachments"]["$each"].append(
                        # document to add to array
                        {
                            "src": str(announcement_body["attachments"][i]["new_src"]),
                            "attachment_type": CheckHttpFileType(
                                str(announcement_body["attachments"][i]["new_src"])
                            ),
                        }
                    )

                elif announcement_body["attachments"][i]["op"] == "delete":
                    update_body_delete["$pull"]["attachments"]["src"]["$in"].append(
                        # id of document to delete from array
                        str(announcement_body["attachments"][i]["old_src"])
                    )

                elif announcement_body["attachments"][i]["op"] == "edit":
                    array_filter.append(
                        # filter to find document to update in array
                        {
                            f"elem{i}.src": str(
                                announcement_body["attachments"][i]["old_src"]
                            )
                        }
                    )
                    # update body for document to update in array
                    update_body_edit["$set"][f"attachments.$[elem{i}].src"] = str(
                        announcement_body["attachments"][i]["new_src"]
                    )

                    update_body_edit["$set"][
                        f"attachments.$[elem{i}].attachment_type"
                    ] = str(
                        CheckHttpFileType(
                            str(announcement_body["attachments"][i]["new_src"])
                        )
                    )

                else:
                    raise Exception.unprocessable_content

        # update each operation
        result = db_client.annoucement_coll.update_one(
            filter=filter, update=update_body_add
        )
        if result.matched_count == 0:
            raise Exception.not_found
        result = db_client.annoucement_coll.update_one(
            filter=filter, update=update_body_delete
        )
        if result.matched_count == 0:
            raise Exception.not_found
        result = db_client.annoucement_coll.update_one(
            filter=filter, update=update_body_edit, array_filters=array_filter
        )
        if result.matched_count == 0:
            raise Exception.not_found
        return True
    except InvalidId:
        raise Exception.bad_request


def remove_course_announcement(course_id: str, announcement_id: str) -> bool:
    try:
        filter = {"_id": ObjectId(announcement_id), "course_id": ObjectId(course_id)}
        result = db_client.annoucement_coll.delete_one(filter=filter)
        if result.deleted_count == 0:
            raise Exception.not_found
        return True
    except InvalidId:
        raise Exception.bad_request
