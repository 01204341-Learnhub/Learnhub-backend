from pydantic import TypeAdapter


from ....dependencies import (
    GenericOKResponse,
    Exception,
    utc_datetime_now,
    mongo_datetime_to_timestamp,
)

from .schemas import (
    AttachmentModelBody,
    GetAssignmentSubmissionResponseModel,
    GetClassAssignmentResponseModel,
    ListAssignmentSubmissionModelBody,
    ListAssignmentSubmissionResponseModel,
    ListClassAssignmentsModelBody,
    ListClassAssignmentsResponseModel,
    PatchAssignmentRequestModel,
    PatchAssignmentSubmissionScoreRequestModel,
    PostClassAssignmentRequestModel,
    PostClassAssignmentResponseModel,
    PutAssignmentSubmitRequestModel,
    PutAssignmentSubmitResponseModel,
    StudentModelBody,
    SubmissionCountModelBody,
)

from .database import (
    create_assignment,
    query_assignments_by_class_id,
    query_list_submission_by_assignment_id,
    query_single_assignment,
    edit_assignment,
    query_single_submission_by_student_id,
    query_student_profile,
    score_submission,
    unsubmit_submission,
    update_submission,
)

from .config import (
    SubmissionStatus,
    AssignmentStatus,
)


# ASSIGNMENTS
def list_assignment_response(class_id: str) -> ListClassAssignmentsResponseModel:
    assignments_cur = query_assignments_by_class_id(class_id)
    assignments = []

    for assg_ in assignments_cur:
        submissions_cur = query_list_submission_by_assignment_id(
            class_id, str(assg_["_id"])
        )
        submit_count = 0
        unsubmit_count = 0
        for submission_ in submissions_cur:
            if submission_["status"] == SubmissionStatus.unsubmit:
                unsubmit_count += 1
            else:
                submit_count += 1

        assignments.append(
            ListClassAssignmentsModelBody(
                assignment_id=str(assg_["_id"]),
                name=assg_["name"],
                group_name=assg_["group_name"],
                last_edit=mongo_datetime_to_timestamp(assg_["last_edit"]),
                due_date=mongo_datetime_to_timestamp(assg_["due_date"]),
                status=assg_["status"],
                max_score=assg_["max_score"],
                text=assg_["text"],
                submission_count=SubmissionCountModelBody(
                    submit_count=submit_count, unsubmit_count=unsubmit_count
                ),
            )
        )
    return ListClassAssignmentsResponseModel(assignments=assignments)


def get_assignment_response(
    class_id: str, assignment_id: str
) -> GetClassAssignmentResponseModel:
    assignment = query_single_assignment(class_id, assignment_id)
    if assignment == None:
        raise Exception.not_found
    ta = TypeAdapter(list[AttachmentModelBody])
    response_body = GetClassAssignmentResponseModel(
        name=assignment["name"],
        group_name=assignment["group_name"],
        last_edit=mongo_datetime_to_timestamp(assignment["last_edit"]),
        due_date=mongo_datetime_to_timestamp(assignment["due_date"]),
        status=assignment["status"],
        max_score=assignment["max_score"],
        text=assignment["text"],
        attachments=ta.validate_python(assignment["attachments"]),
    )
    return response_body


def post_assignment_request(
    class_id: str, request: PostClassAssignmentRequestModel
) -> PostClassAssignmentResponseModel:
    inserted_id = create_assignment(class_id, request)
    if request.due_date <= mongo_datetime_to_timestamp(utc_datetime_now()):
        err = Exception.unprocessable_content
        err.__setattr__("detail", "required due_date to be later that present")
    return PostClassAssignmentResponseModel(assignment_id=inserted_id)


def patch_assignment_request(
    class_id: str, assignment_id: str, patch_body: PatchAssignmentRequestModel
):
    response = edit_assignment(
        class_id=class_id, assignment_id=assignment_id, patch_body_=patch_body
    )
    return GenericOKResponse


# SUBMISSION
def list_assignment_submissions_response(
    class_id: str, assignment_id: str
) -> ListAssignmentSubmissionResponseModel:
    submissions_cur = query_list_submission_by_assignment_id(class_id, assignment_id)
    # assign
    submissions = []
    for sub_ in submissions_cur:
        student = query_student_profile(str(sub_["student_id"]))

        submissions.append(
            ListAssignmentSubmissionModelBody(
                status=sub_["status"],
                score=sub_["score"],
                submission_date=mongo_datetime_to_timestamp(sub_["submission_date"]),
                student=StudentModelBody(**student),
            )
        )

    return ListAssignmentSubmissionResponseModel(submissions=submissions)


def get_assignment_submission_response(
    class_id: str, assignment_id: str, student_id: str
) -> GetAssignmentSubmissionResponseModel:
    submission = query_single_submission_by_student_id(
        class_id, assignment_id, student_id
    )
    if submission == None:
        raise Exception.not_found
    student = query_student_profile(str(submission["student_id"]))

    ta = TypeAdapter(list[AttachmentModelBody])

    response = GetAssignmentSubmissionResponseModel(
        status=submission["status"],
        score=submission["score"],
        student=StudentModelBody(**student),
        submission_date=mongo_datetime_to_timestamp(submission["submission_date"]),
        attachments=ta.validate_python(submission["attachments"]),
    )
    return response


def patch_assignment_submission_score_request(
    class_id: str,
    assignment_id: str,
    student_id: str,
    request: PatchAssignmentSubmissionScoreRequestModel,
):
    score_submission(class_id, assignment_id, student_id, request.score)
    return GenericOKResponse


def put_assignment_submit_request(
    class_id: str,
    assignment_id: str,
    student_id: str,
    request: PutAssignmentSubmitRequestModel,
) -> PutAssignmentSubmitResponseModel:
    student_id = update_submission(class_id, assignment_id, student_id, request)
    return PutAssignmentSubmitResponseModel(student_id=student_id)


def patch_assignment_unsubmit_request(
    class_id: str, assignment_id: str, student_id: str
):
    unsubmit_submission(class_id, assignment_id, student_id)
    return GenericOKResponse
