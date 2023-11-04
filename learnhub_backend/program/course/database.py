from pymongo.cursor import Cursor
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
from bson.errors import InvalidId

from learnhub_backend.quiz.database import query_quiz

from ..database import db_client

from .schemas import (
    PostCourseRequestModel,
    PostCourseChapterRequestModel,
    PatchCourseChapterRequestModel,
    PatchCourseLessonRequestModel,
    PostCourseLessonRequestModel,
    PatchCourseRequestModel,
)

from ...dependencies import (
    Exception,
    utc_datetime_now,
    timestamp_to_utc_datetime,
    student_type,
    teacher_type,
    course_type,
    class_type,
)

from ...dependencies import student_type


# AUXILARY
def query_teacher_by_id(id: str | ObjectId):
    try:
        filter = {"type": teacher_type, "_id": id}
        if type(id) == str:
            filter["_id"] = ObjectId(id)
        teacher = db_client.user_coll.find_one(filter=filter)
        return teacher

    except InvalidId:
        raise Exception.bad_request


def query_list_tags_by_id(ids: list[str | ObjectId]):
    try:
        object_ids = list(map(ObjectId, ids))

        filter = {"_id": {"$in": object_ids}}
        tags = db_client.tag_coll.find(filter)
        return tags

    except InvalidId:
        raise Exception.bad_request


# COURSE
def query_list_courses(skip: int = 0, limit: int = 100) -> Cursor:
    try:
        courses_cursor = db_client.course_coll.find(skip=skip, limit=limit)
        return courses_cursor
    except InvalidId:
        raise Exception.bad_request


def query_list_popular_courses() -> dict[str, int]:
    now = utc_datetime_now()
    last_month = now.replace(month=now.month - 1)
    transaction_filter = {
        "purchase_list": {
            "$elemMatch": {
                "type": course_type,
            }
        },
        "purchase_time": {"$gte": last_month},
    }
    transactions_cur = db_client.transaction_coll.find(transaction_filter)

    popular_courses: dict[str, int] = {}

    for _transac in transactions_cur:
        for _pur in _transac["purchase_list"]:
            if (
                _pur["type"] == course_type
                and str(_pur["program_id"]) not in popular_courses
            ):
                popular_courses[str(_pur["program_id"])] = 1
            elif _pur["type"] == course_type:
                popular_courses[str(_pur["program_id"])] += 1

    return popular_courses


def query_course(course_id: str):
    try:
        filter = {"_id": ObjectId(course_id)}
        course = db_client.course_coll.find_one(filter=filter)
        return course
    except InvalidId:
        raise Exception.bad_request


def create_course(course_body: PostCourseRequestModel) -> InsertOneResult:
    try:
        # Check valid teacher
        teacher_filter = {"type": teacher_type, "_id": ObjectId(course_body.teacher_id)}
        teacher_result = db_client.user_coll.find_one(filter=teacher_filter)
        if teacher_result == None:
            raise Exception.unprocessable_content

        # Check valid tag
        for tag_id in course_body.tag_ids:
            tag_result = db_client.tag_coll.find_one(ObjectId(tag_id))
            if tag_result == None:
                raise Exception.unprocessable_content

        body = {
            "name": course_body.name,
            "teacher_id": ObjectId(course_body.teacher_id),
            "description": course_body.description,
            "created_date": utc_datetime_now(),
            "course_pic": str(course_body.course_pic),
            "student_count": 0,
            "rating": 0,
            "review_count": 0,
            "price": course_body.price,
            "course_objective": course_body.course_objective,
            "course_requirement": course_body.course_requirement,
            "difficulty_level": course_body.difficulty_level,
            "tags": list(map(ObjectId, course_body.tag_ids)),
            "total_video_length": 0,
            "chapter_count": 0,
            "file_count": 0,
            "quiz_count": 0,
            "video_count": 0,
            "status": "started",  # TODO: add not deployed status
        }

        insert_course_result = db_client.course_coll.insert_one(document=body)
        if insert_course_result.inserted_id == None:
            raise Exception.internal_server_error

        # Add teacher owned program
        push_content = {
            "owned_programs": {
                "type": course_type,
                "program_id": insert_course_result.inserted_id,
            }
        }
        push_result = db_client.user_coll.update_one(
            teacher_filter, {"$push": push_content}
        )
        if push_result.matched_count == 0:
            raise Exception.internal_server_error
        return insert_course_result

    except InvalidId:
        raise Exception.bad_request


def edit_course(course_id: str, course_body: PatchCourseRequestModel):
    try:
        filter = {"_id": ObjectId(course_id)}

        # prepare update body
        set_content = dict()
        push_content = dict()
        pull_content = dict()
        if course_body.name != None:
            set_content["name"] = course_body.name
        if course_body.course_pic != None:
            set_content["course_pic"] = str(course_body.course_pic)
        if course_body.price != None:
            set_content["price"] = course_body.price
        if course_body.description != None:
            set_content["description"] = course_body.description
        if course_body.course_requirement != None:
            set_content["course_requirement"] = course_body.course_requirement
        if course_body.difficulty_level != None:
            set_content["difficulty_level"] = course_body.difficulty_level

        # course objective
        if course_body.course_objective != None:
            for objective_ in course_body.course_objective:
                if objective_.op == "add":
                    if "course_objective" not in push_content:
                        push_content["course_objective"] = {}
                        push_content["course_objective"]["$each"] = []
                    push_content["course_objective"]["$each"].append(objective_.value)
                elif objective_.op == "remove":
                    if "course_objective" not in pull_content:
                        pull_content["course_objective"] = {}
                        pull_content["course_objective"]["$in"] = []
                    pull_content["course_objective"]["$in"].append(objective_.value)

        # tags
        if course_body.tag != None:
            #  Check duplicate tags
            _course_tag_filter = {
                "_id": ObjectId(course_id),
                "tags": ObjectId(course_body.tag.tag_id),
            }

            tag_filter = {"_id": ObjectId(course_body.tag.tag_id)}
            tag = db_client.tag_coll.find_one(tag_filter)
            if tag == None:
                err = Exception.unprocessable_content
                err.__setattr__("detail", "Invalid tag_id")
                raise err

            if course_body.tag.op == "add":
                _course_tag_check_result = db_client.course_coll.find_one(
                    _course_tag_filter
                )
                if _course_tag_check_result != None:
                    err = Exception.unprocessable_content
                    err.__setattr__("detail", "duplicate course's tag")
                    raise err
                push_content["tags"] = ObjectId(course_body.tag.tag_id)
            elif course_body.tag.op == "remove":
                pull_content["tags"] = dict()
                pull_content["tags"]["$in"] = [ObjectId(course_body.tag.tag_id)]

        # mongo doesn't allow multi operation edit
        patch_result = None
        if len(set_content) != 0:
            patch_result = db_client.course_coll.update_one(
                filter, {"$set": set_content}
            )
        if len(push_content) != 0:
            patch_result = db_client.course_coll.update_one(
                filter, {"$push": push_content}
            )
        if len(pull_content) != 0:
            patch_result = db_client.course_coll.update_one(
                filter, {"$pull": pull_content}
            )

        if patch_result == None:
            raise Exception.internal_server_error
    except InvalidId:
        raise Exception.bad_request


def student_is_own_program(student_id: str, _type: str, program_id: str) -> bool:
    owned = False
    result = None
    if _type == course_type:
        filter = {
            "_id": ObjectId(student_id),
            "owned_programs.program_id": ObjectId(program_id),
            "owned_programs.type": course_type,
        }
        result = db_client.user_coll.find_one(filter)
    elif _type == class_type:
        filter = {
            "_id": ObjectId(student_id),
            "owned_programs.program_id": ObjectId(program_id),
            "owned_programs.type": class_type,
        }
        result = db_client.user_coll.find_one(filter)

    if result != None:
        owned = True
    return owned


def review_course(course_id: str, student_id: str, rating: float) -> str:
    _course = query_course(course_id)
    if _course == None:
        err = Exception.not_found
        err.__setattr__("detail", "Course not found")
        raise err

    review_filter = {
        "student_id": ObjectId(student_id),
        "course_id": ObjectId(course_id),
    }
    review_result = db_client.course_review_coll.find_one(review_filter)

    filter = {"_id": ObjectId(course_id)}
    set_content = dict()
    if review_result == None:  # First review
        current_rating_full = _course["rating"] * _course["review_count"]
        new_rating = (current_rating_full + rating) / (_course["review_count"] + 1)
        set_content = {
            "rating": new_rating,
            "review_count": _course["review_count"] + 1,
        }
    else:  # Change review
        current_rating_full = _course["rating"] * _course["review_count"]
        new_rating = (current_rating_full + rating - review_result["rating"]) / (
            _course["review_count"]
        )
        set_content = {
            "rating": new_rating,
        }

    result = db_client.course_coll.update_one(filter, {"$set": set_content})
    if result.matched_count == 0:
        raise Exception.not_found

    if review_result == None:  # First review
        body = {
            "course_id": ObjectId(course_id),
            "student_id": ObjectId(student_id),
            "rating": rating,
        }
        insert_res = db_client.course_review_coll.insert_one(body)
        return str(insert_res.inserted_id)
    else:  # Change review
        set_review = {"rating": rating}
        patch_res = db_client.course_review_coll.find_one_and_update(
            review_filter, {"$set": set_review}
        )
        return str(patch_res["_id"])


# CHAPTER
def query_list_course_chapters(course_id: str, skip: int = 0, limit: int = 100) -> list:
    try:
        chapters_cursor = db_client.chapter_coll.find(
            {"course_id": ObjectId(course_id)}, skip=skip, limit=limit
        )
        chapters = []
        for chapter in chapters_cursor:
            chapter["chapter_id"] = str(chapter["_id"])
            chapters.append(chapter)
        return chapters
    except InvalidId:
        raise Exception.bad_request


def create_course_chapter(course_id: str, chapter_body: PostCourseChapterRequestModel):
    try:
        chapter_body_to_inserted = chapter_body.model_dump()
        chapter_body_to_inserted["course_id"] = ObjectId(course_id)
        chapter_body_to_inserted["description"] = chapter_body.description
        chapter_body_to_inserted["chapter_length"] = 0
        chapter_body_to_inserted["lesson_count"] = 0

        # No matching course
        valid_course_id_filter = {"_id": ObjectId(course_id)}
        result = db_client.course_coll.find_one(filter=valid_course_id_filter)
        if result == None:
            raise Exception.unprocessable_content

        response_chapter_num = (
            db_client.chapter_coll.find(
                {"course_id": ObjectId(course_id)}, {"chapter_num": True}
            )
            .sort([("chapter_num", -1)])
            .limit(1)
        )
        try:
            chapter_body_to_inserted["chapter_num"] = (
                response_chapter_num.next()["chapter_num"] + 1
            )
        except StopIteration:
            chapter_body_to_inserted["chapter_num"] = 1

        response = db_client.chapter_coll.insert_one(chapter_body_to_inserted)

        # increase course chapter count
        course_filter = {"_id": ObjectId(course_id)}
        course_update = {"$inc": {"chapter_count": 1}}
        update_response = db_client.course_coll.update_one(
            filter=course_filter, update=course_update
        )

        return response
    except InvalidId:
        raise Exception.bad_request


def query_course_chapter(chapter_id: str):
    try:
        queried_chapter = db_client.chapter_coll.find_one({"_id": ObjectId(chapter_id)})
        if queried_chapter != None:
            queried_chapter["chapter_id"] = str(queried_chapter["_id"])
            queried_chapter["course_id"] = str(queried_chapter["course_id"])
        return queried_chapter
    except InvalidId:
        raise Exception.bad_request


def edit_course_chapter(
    chapter_id: str, chapter_to_edit: PatchCourseChapterRequestModel
):
    try:
        # print(chapter_to_edit)
        filter_chapter = {"_id": ObjectId(chapter_id)}
        chapter_to_edit_2 = {"$set": chapter_to_edit.model_dump(exclude_unset=True)}
        response = db_client.chapter_coll.update_one(filter_chapter, chapter_to_edit_2)
        if response.matched_count == 0:
            raise Exception.not_found
        return response
    except InvalidId:
        raise Exception.bad_request


def delete_course_chapter(chapter_id: str, course_id: str):
    try:
        chapter_delete_filter = {"_id": ObjectId(chapter_id)}
        delete_response = db_client.chapter_coll.find_one_and_delete(
            filter=chapter_delete_filter, projection={"chapter_num": True}
        )
        if delete_response == None:  # Deletion Failed.
            raise Exception.not_found

        chapter_num_threshold = delete_response["chapter_num"]
        chapter_update_filter = {
            "course_id": ObjectId(course_id),
            "chapter_num": {"$gt": chapter_num_threshold},
        }
        update_chapter = {"$inc": {"chapter_num": -1}}
        update_response = db_client.chapter_coll.update_many(
            filter=chapter_update_filter, update=update_chapter
        )

        # update course
        course_filter = {
            "course_id": ObjectId(course_id),
        }
        update_course = {
            "$inc": {
                "chapter_count": -1,
                "video_count": 0,
                "total_video_length": 0,
                "file_count": 0,
                "quiz_count": 0,
            }
        }

        lesson_filter = {
            "course_id": ObjectId(course_id),
            "chapter_id": ObjectId(chapter_id),
        }
        # find lessons
        lessons_cursor = db_client.lesson_coll.find(filter=lesson_filter)
        for lesson in lessons_cursor:
            if lesson["lesson_type"] == "video":
                update_course["$inc"]["video_count"] -= 1
                update_course["$inc"]["total_video_length"] -= lesson["lesson_length"]
            elif lesson["lesson_type"] == "file":
                update_course["$inc"]["file_count"] -= 1
            elif lesson["lesson_type"] == "quiz":
                update_course["$inc"]["quiz_count"] -= 1

        # lesson delete
        delete_response = db_client.lesson_coll.delete_many(filter=lesson_filter)

        course_response = db_client.course_coll.update_one(
            filter=course_filter, update=update_course
        )
        if course_response.matched_count == 0:
            raise Exception.internal_server_error

        return
    except InvalidId:
        raise Exception.bad_request


# LESSON
def query_list_course_lessons(
    course_id: str, chapter_id: str, skip: int = 0, limit: int = 100
) -> list:
    try:
        filter = {"course_id": ObjectId(course_id), "chapter_id": ObjectId(chapter_id)}
        lessons_cursor = db_client.lesson_coll.find(
            filter=filter, skip=skip, limit=limit
        )
        lessons = []
        for lesson in lessons_cursor:
            lesson["lesson_id"] = str(lesson["_id"])
            lessons.append(lesson)
        return lessons
    except InvalidId:
        raise Exception.bad_request


def query_course_lesson(course_id: str, chapter_id: str, lesson_id: str) -> dict | None:
    try:
        filter = {
            "_id": ObjectId(lesson_id),
            "course_id": ObjectId(course_id),
            "chapter_id": ObjectId(chapter_id),
        }
        lesson = db_client.lesson_coll.find_one(filter=filter)
        if lesson != None:
            lesson["lesson_id"] = str(lesson["_id"])
        return lesson
    except InvalidId:
        raise Exception.bad_request


def create_course_lesson(
    course_id: str, chapter_id: str, request: PostCourseLessonRequestModel
) -> str:
    try:
        # Check for valid course and chapter
        valid_course_filter = {"_id": ObjectId(course_id)}
        course_result = db_client.course_coll.find_one(filter=valid_course_filter)
        if course_result == None:
            raise Exception.unprocessable_content
        valid_chapter_filter = {"_id": ObjectId(chapter_id)}
        chapter_result = db_client.chapter_coll.find_one(filter=valid_chapter_filter)

        if chapter_result == None:
            raise Exception.unprocessable_content

        body = dict()
        body["course_id"] = ObjectId(course_id)
        body["chapter_id"] = ObjectId(chapter_id)
        body["name"] = request.name
        body["lesson_length"] = request.lesson_length
        body["lesson_type"] = request.lesson_type
        body["src"] = request.src

        filter = {"course_id": ObjectId(course_id), "chapter_id": ObjectId(chapter_id)}
        while True:
            # Auto increment lesson_num
            cursor = (
                db_client.lesson_coll.find(filter, {"lesson_num": True})
                .sort([("lesson_num", -1)])
                .limit(1)
            )
            try:
                body["lesson_num"] = cursor.next()["lesson_num"] + 1
            except StopIteration:
                body["lesson_num"] = 1
            break

        object_id = db_client.lesson_coll.insert_one(body)

        # chapter
        chapter_filter = {"_id": ObjectId(chapter_id)}
        chapter_update = {
            "$inc": {"chapter_length": request.lesson_length, "lesson_count": 1}
        }
        result = db_client.chapter_coll.update_one(
            filter=chapter_filter, update=chapter_update
        )

        # course
        course_update = dict()
        course_filter = {"_id": ObjectId(course_id)}
        if request.lesson_type == "video":
            course_update = {
                "$inc": {"total_video_length": request.lesson_length, "video_count": 1}
            }
        elif request.lesson_type == "file":  # other filetype count as file
            course_update = {"$inc": {"file_count": 1}}
        elif request.lesson_type == "quiz":
            course_update = {"$inc": {"quiz_count": 1}}
        # elif request.lesson_type == "doc":
        # TODO: inc doc

        result = db_client.course_coll.update_one(
            filter=course_filter, update=course_update
        )

        _update_student_progress(
            course_id, chapter_id, str(object_id.inserted_id), request
        )

        return str(object_id.inserted_id)
    except InvalidId:
        raise Exception.bad_request


def _update_student_progress(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
    request: PostCourseLessonRequestModel,
):
    progress_filter = {"course_id": ObjectId(course_id)}
    progress_lesson_body = {
        "lesson_id": ObjectId(lesson_id),
        "chapter_id": ObjectId(chapter_id),
        "finished": False,
        "lesson_completed": 0,
    }
    result = db_client.course_progress_coll.update_many(
        progress_filter, {"$push": {"lessons": progress_lesson_body}}
    )
    if request.lesson_type == "quiz":  # should add student quiz results
        own_course_filter = {
            "type": student_type,
            "owned_programs.program_id": ObjectId(course_id),
            "owned_programs.type": "course",
        }
        students_cur = db_client.user_coll.find(own_course_filter)

        quiz = db_client.quiz_coll.find_one(ObjectId(request.src))
        if quiz == None:
            raise Exception.internal_server_error
        for student in students_cur:
            body = {
                "score": 0,
                "problems": [],
                "status": "not started",
                "quiz_id": ObjectId(request.src),
                "student_id": student["_id"],  # already object id
            }
            for problem in quiz["problems"]:
                body["problems"].append(
                    {
                        "problem_num": problem["problem_num"],
                        "is_correct": False,
                        "answer": {
                            "answer_a": False,
                            "answer_b": False,
                            "answer_c": False,
                            "answer_d": False,
                            "answer_e": False,
                            "answer_f": False,
                        },
                    }
                )
            _ = db_client.quiz_result_coll.insert_one(body)


def edit_course_lesson(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
    request: PatchCourseLessonRequestModel,
):
    try:
        filter = {
            "_id": ObjectId(lesson_id),
            "course_id": ObjectId(course_id),
            "chapter_id": ObjectId(chapter_id),
        }

        original = db_client.lesson_coll.find_one(filter=filter)
        if original == None:
            raise Exception.not_found

        update_body = {}
        if request.name != None:
            update_body["name"] = request.name
        if request.lesson_length != None:
            update_body["lesson_length"] = request.lesson_length
        if request.src != None:
            update_body["src"] = str(request.src)

        update = {"$set": update_body}
        result = db_client.lesson_coll.update_one(
            filter=filter, update=update
        )  # returns original doc
        if result.matched_count == 0:
            raise Exception.not_found

        if (
            request.lesson_length != None
            and request.lesson_length != original["lesson_length"]
        ):
            chapter_filter = {"_id": ObjectId(chapter_id)}
            chapter_update = {
                "$inc": {
                    "chapter_length": request.lesson_length - original["lesson_length"]
                }
            }
            chapter_result = db_client.chapter_coll.update_one(
                filter=chapter_filter, update=chapter_update
            )

            if original["lesson_type"] == "video":
                course_filter = {"_id": ObjectId(course_id)}
                course_update = {
                    "$inc": {
                        "total_video_length": request.lesson_length
                        - original["lesson_length"]
                    }
                }
                course_result = db_client.course_coll.update_one(
                    filter=course_filter, update=course_update
                )

    except InvalidId:
        raise Exception.bad_request


def remove_course_lesson(
    course_id: str,
    chapter_id: str,
    lesson_id: str,
):
    try:
        delete_filter = {
            "_id": ObjectId(lesson_id),
            "course_id": ObjectId(course_id),
            "chapter_id": ObjectId(chapter_id),
        }
        original = db_client.lesson_coll.find_one_and_delete(delete_filter)
        if original == None:  # Deletion Failed.
            raise Exception.not_found

        # update lesson num
        lesson_num_threshold = original["lesson_num"]

        update_filter = {
            "course_id": ObjectId(course_id),
            "chapter_id": ObjectId(chapter_id),
            "lesson_num": {"$gt": lesson_num_threshold},
        }

        update_body = {"$inc": {"lesson_num": -1}}
        result = db_client.lesson_coll.update_many(
            filter=update_filter, update=update_body
        )

        # update chapter
        chapter_filter = {"_id": ObjectId(chapter_id)}
        chapter_update = {
            "$inc": {"lesson_count": -1, "chapter_length": -original["lesson_length"]}
        }
        result = db_client.chapter_coll.update_one(chapter_filter, chapter_update)

        # update course
        course_filter = {"_id": ObjectId(course_id)}
        match original["lesson_type"]:
            case "video":
                course_update = {
                    "$inc": {
                        "video_count": -1,
                        "total_video_length": -original["lesson_length"],
                    }
                }
            case "file":
                course_update = {
                    "$inc": {
                        "file_count": -1,
                    }
                }
            case "quiz":
                course_update = {
                    "$inc": {
                        "quiz_count": -1,
                    }
                }
            case _:
                course_update = dict()
        result = db_client.course_coll.update_one(course_filter, course_update)

    except InvalidId:
        raise Exception.bad_request
