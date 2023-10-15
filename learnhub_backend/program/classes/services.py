from pydantic import HttpUrl, TypeAdapter

from learnhub_backend.dependencies import (
    GenericOKResponse,
    mongo_datetime_to_timestamp,
    utc_datetime_now,
    utc_datetime,
)

from .database import (
    create_class,
    create_thread_reply,
    edit_class,
    get_student_by_id,
    query_list_classes,
    get_teacher_by_id,
    query_list_students_by_class,
    query_list_tags_by_id,
    query_class,
    query_list_thread_replies_by_class,
    query_list_thread_replies_by_thread,
    query_list_threads,
    create_thread,
    query_thread,
    edit_thread,
)
from .schemas import (
    ListClassStudentsResponseModel,
    ListClassesModelBody,
    ListClassesResponseModel,
    GetClassResponseModel,
    PatchClassRequestModel,
    PostClassRequestModel,
    PostClassResponseModel,
    ListThreadModelBody,
    ListThreadResponseModel,
    PostThreadReplyRequestModel,
    PostThreadReplyResponseModel,
    PostThreadRequestModel,
    PostThreadResponseModel,
    GetThreadResponseModel,
    PatchThreadRequestModel,
    ReplyModelBody,
    StudentModelBody,
    UserReplyModelBody,
)

from ...dependencies import (
    Exception,
    student_type,
    teacher_type,
    class_type,
    course_type,
)


# CLASSES
def list_classes_response(skip: int, limit: int) -> ListClassesResponseModel:
    classes_corsor = query_list_classes(skip=skip, limit=limit)
    quried_classes = []
    for class_ in classes_corsor:
        if utc_datetime(class_["registration_ended_date"]) < utc_datetime_now():
            continue  # continue if you can't buy class anymore
        class_["class_id"] = str(class_["_id"])
        class_["teacher"] = get_teacher_by_id(str(class_["teacher_id"]))
        class_["tags"] = query_list_tags_by_id(class_["tags"])
        class_["registration_ended_date"] = mongo_datetime_to_timestamp(
            class_["registration_ended_date"]
        )
        class_["open_date"] = mongo_datetime_to_timestamp(class_["open_date"])
        class_["class_ended_date"] = mongo_datetime_to_timestamp(
            class_["class_ended_date"]
        )
        quried_classes.append(class_)

    ta = TypeAdapter(list[ListClassesModelBody])
    response_body = ListClassesResponseModel(classes=ta.validate_python(quried_classes))
    return response_body


def get_class_response(class_id: str) -> GetClassResponseModel:
    class_ = query_class(class_id=class_id)
    if class_ == None:
        raise Exception.not_found

    class_["class_id"] = str(class_["_id"])
    class_["teacher"] = get_teacher_by_id(str(class_["teacher_id"]))
    class_["tags"] = query_list_tags_by_id(class_["tags"])
    class_["registration_ended_date"] = mongo_datetime_to_timestamp(
        class_["registration_ended_date"]
    )
    class_["open_date"] = mongo_datetime_to_timestamp(class_["open_date"])
    class_["class_ended_date"] = mongo_datetime_to_timestamp(class_["class_ended_date"])
    for i in range(len(class_["schedules"])):
        # print(class_["schedules"][i]["start"])
        class_["schedules"][i]["start"] = mongo_datetime_to_timestamp(
            class_["schedules"][i]["start"]
        )
        class_["schedules"][i]["end"] = mongo_datetime_to_timestamp(
            class_["schedules"][i]["end"]
        )

    return GetClassResponseModel(**class_)


def post_class_request(request: PostClassRequestModel) -> PostClassResponseModel:
    class_id = create_class(request)
    return PostClassResponseModel(class_id=class_id)


def patch_class_request(class_id: str, request: PatchClassRequestModel):
    edit_class(class_id, request)
    return GenericOKResponse


# STUDENTS
def list_class_students_response(class_id: str) -> ListClassStudentsResponseModel:
    students_cur = query_list_students_by_class(class_id)
    students: list[StudentModelBody] = []
    for _student in students_cur:
        students.append(
            StudentModelBody(
                student_id=str(_student["_id"]),
                name=_student["fullname"],
                profile_pic=HttpUrl(_student["profile_pic"]),
            )
        )
    return ListClassStudentsResponseModel(students=students)


# THREADS
def list_threads_response(class_id: str, skip: int, limit: int):
    thread_cursor = query_list_threads(class_id=class_id, skip=skip, limit=limit)
    threads = []
    for thread in thread_cursor:
        replies: list[ReplyModelBody] = []
        replies_cur = query_list_thread_replies_by_class(class_id)
        for _reply in replies_cur:
            if _reply["user"]["user_type"] == student_type:
                _user = get_student_by_id(_reply["user"]["user_id"])
            elif _reply["user"]["user_type"] == teacher_type:
                _user = get_teacher_by_id(_reply["user"]["user_id"])
            else:
                raise Exception.unprocessable_content
            replies.append(
                ReplyModelBody(
                    text=_reply["text"],
                    reply_date=mongo_datetime_to_timestamp(_reply["reply_date"]),
                    user=UserReplyModelBody(
                        user_id=str(_reply["user"]["user_id"]),
                        user_type=_reply["user"]["user_type"],
                        name=_user["fullname"],
                        profile_pic=HttpUrl(_user["profile_pic"]),
                    ),
                )
            )

        thread["thread_id"] = str(thread["_id"])
        thread["teacher"] = get_teacher_by_id(str(thread["teacher_id"]))
        thread["last_edit"] = mongo_datetime_to_timestamp(thread["last_edit"])
        thread["replies"] = replies
        threads.append(thread)

    ta = TypeAdapter(list[ListThreadModelBody])
    return ListThreadResponseModel(threads=ta.validate_python(threads))


def post_thread_request(class_id: str, thread_body: PostThreadRequestModel):
    thread_id = create_thread(class_id=class_id, thread_body=thread_body)
    return PostThreadResponseModel(thread_id=thread_id)


def get_thread_response(class_id: str, thread_id: str):
    quried_thread = query_thread(class_id=class_id, thread_id=thread_id)
    if quried_thread == None:
        raise Exception.not_found
    quried_thread["teacher"] = get_teacher_by_id(str(quried_thread["teacher_id"]))
    quried_thread["last_edit"] = mongo_datetime_to_timestamp(
        quried_thread["last_edit"]
    )  # make timestamp timezone aware that db return utc time
    reply_cur = query_list_thread_replies_by_thread(class_id, thread_id)
    replies: list[ReplyModelBody] = []
    for _reply in reply_cur:
        if _reply["user"]["user_type"] == student_type:
            _user = get_student_by_id(_reply["user"]["user_id"])
        elif _reply["user"]["user_type"] == teacher_type:
            _user = get_teacher_by_id(_reply["user"]["user_id"])
        else:
            raise Exception.unprocessable_content
        replies.append(
            ReplyModelBody(
                text=_reply["text"],
                reply_date=mongo_datetime_to_timestamp(_reply["reply_date"]),
                user=UserReplyModelBody(
                    user_id=str(_reply["user"]["user_id"]),
                    user_type=_reply["user"]["user_type"],
                    name=_user["fullname"],
                    profile_pic=HttpUrl(_user["profile_pic"]),
                ),
            )
        )
    quried_thread["replies"] = replies
    return GetThreadResponseModel(**quried_thread)


def patch_thread_request(
    class_id: str, thread_id: str, thread_body: PatchThreadRequestModel
):
    edit_thread(class_id=class_id, thread_id=thread_id, thread_body=thread_body)
    return GenericOKResponse


# REPLY
def post_thread_reply_request(
    class_id: str, thread_id: str, request: PostThreadReplyRequestModel
) -> PostThreadReplyResponseModel:
    thread_reply_id = create_thread_reply(class_id, thread_id, request)
    return PostThreadReplyResponseModel(thread_reply_id=str(thread_reply_id))
