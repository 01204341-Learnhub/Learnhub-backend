from learnhub_backend.dependencies import GenericOKResponse, Exception
from .database import create_quiz, query_quiz, query_quiz_result, edit_quiz_result
from .schemas import (
    GetQuizResponseModel,
    GetQuizResultResponseModel,
    PatchQuizResultRequestModel,
    PatchQuizResultResponseModel,
    PostQuizRequestModel,
    PostQuizResponseModel,
)


# QUIZ
def get_quiz_response(quiz_id: str):
    queried_quiz = query_quiz(
        quiz_id=quiz_id,
    )
    return GetQuizResponseModel(**queried_quiz)


def post_quiz_request(request: PostQuizRequestModel) -> PostQuizResponseModel:
    quiz_id = create_quiz(request)
    return PostQuizResponseModel(quiz_id=quiz_id)


def get_quiz_result_response(quiz_id: str, student_id: str):
    response_body = query_quiz(
        quiz_id=quiz_id,
    )

    queried_quiz_result = query_quiz_result(quiz_id=quiz_id, student_id=student_id)
    response_body["status"] = queried_quiz_result["status"]
    response_body["score"] = queried_quiz_result["score"]

    # make problem result

    # sort problems in quiz_result by problem_num
    problem_results_list = sorted(
        queried_quiz_result["problems"], key=lambda x: x["problem_num"]
    )

    for i in range(len(response_body["problems"])):
        # check if the problem_num is the same
        if (
            i + 1 == problem_results_list[i]["problem_num"]
            and i + 1 == response_body["problems"][i]["problem_num"]
        ):
            response_body["problems"][i]["answer"] = problem_results_list[i]["answer"]
        else:
            raise Exception.internal_server_error
    return GetQuizResultResponseModel(**response_body)


def patch_quiz_result_response(
    quiz_id: str, student_id: str, answers_body: PatchQuizResultRequestModel
):
    # TODO: make some parameter optional
    answers_body = answers_body.model_dump()
    # cannot redo quiz result
    if answers_body["status"] == "not started":
        raise Exception.bad_request

    # cannot redo quiz result
    check_quiz_result = query_quiz_result(quiz_id=quiz_id, student_id=student_id)
    if check_quiz_result["status"] == "finished":
        raise Exception.bad_request

    for j in range(len(check_quiz_result["problems"])):
        if check_quiz_result["problems"][j]["is_correct"] == True:
            pass

    response_body = {"answer_responses": []}

    # check all answers
    queried_quiz = query_quiz(quiz_id=quiz_id)
    score_inc = len(answers_body["answers"])
    for i in range(len(answers_body["answers"])):
        for j in range(len(check_quiz_result["problems"])):
            # in same problem_num do not increase score if correct already
            if (
                answers_body["answers"][i]["problem_num"]
                == check_quiz_result["problems"][j]["problem_num"]
            ) and check_quiz_result["problems"][j]["is_correct"] == True:
                score_inc -= 1
                # print("no increase score")

        for j in range(len(queried_quiz["problems"])):
            # in same problem_num
            if (
                answers_body["answers"][i]["problem_num"]
                == queried_quiz["problems"][j]["problem_num"]
            ):
                response_body["answer_responses"].append(queried_quiz["problems"][j])
                # check answer
                answers_body["answers"][i]["is_correct"] = True
                for answer_key in answers_body["answers"][i]["answer"].keys():
                    if (
                        answers_body["answers"][i]["answer"][answer_key]
                        != queried_quiz["problems"][j]["correct_answer"][answer_key]
                    ):
                        # wrong answer
                        score_inc -= 1
                        answers_body["answers"][i]["is_correct"] = False
                        break

    edit_quiz_result(
        quiz_id=quiz_id,
        student_id=student_id,
        score_inc=score_inc,
        answers_body=answers_body,
    )
    print(score_inc)
    return PatchQuizResultResponseModel(**response_body)
