from learnhub_backend.dependencies import GenericOKResponse, Exception
from .database import query_quiz, query_quiz_result
from .schemas import GetQuizResponseModel, GetQuizResultResponseModel


def get_quiz_response(quiz_id: str):
    queried_quiz = query_quiz(
        quiz_id=quiz_id,
    )
    return GetQuizResponseModel(**queried_quiz)


def get_quiz_result_response(quiz_id: str, student_id: str):

    response_body = query_quiz(
        quiz_id=quiz_id,
    )

    queried_quiz_result = query_quiz_result(quiz_id=quiz_id, student_id=student_id)
    response_body["status"] = queried_quiz_result["status"]
    response_body["score"] = queried_quiz_result["score"]

    #make problem result

    #sort problems in quiz_result by problem_num
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
