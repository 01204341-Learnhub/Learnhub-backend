from datetime import datetime
from typing import Any
from pydantic import BaseModel, HttpUrl, validator


# QUIZ
class ChoiceModelBody(BaseModel):
    choice_a: str
    choice_b: str
    choice_c: str
    choice_d: str
    choice_e: str
    choice_f: str


class AnswerModelBody(BaseModel):
    answer_a: bool
    answer_b: bool
    answer_c: bool
    answer_d: bool
    answer_e: bool
    answer_f: bool


class GetQuizProblemModelBody(BaseModel):
    problem_num: int
    question: str
    multiple_correct_answers: bool
    choice: ChoiceModelBody


class GetQuizResponseModel(BaseModel):
    name: str
    description: str
    time_limit: int
    quiz_pic: HttpUrl
    problems: list[GetQuizProblemModelBody]


class PostQuizProblemModelBody(BaseModel):
    problem_num: int
    question: str
    multiple_correct_answers: bool
    choice: ChoiceModelBody
    correct_answer: AnswerModelBody
    explanation: str

    @validator("correct_answer")
    def choice_validator(cls, v: AnswerModelBody , values, **kwargs):
        if "multiple_correct_answers" in values and values["multiple_correct_answers"] == False:
            answer_count = 0

            for answer in v.dict().values():
                if answer == True:
                    answer_count += 1
            if answer_count > 1:
                raise ValueError("Multiple correct answers are not allowed")
        return v



class PostQuizRequestModel(BaseModel):
    name: str
    description: str
    time_limit: int
    quiz_pic: HttpUrl
    problems: list[PostQuizProblemModelBody]


class PostQuizResponseModel(BaseModel):
    quiz_id: str


# QUIZ RESULT
class GetQuizResultProblemModelBody(BaseModel):
    problem_num: int
    answer: AnswerModelBody
    correct_answer: AnswerModelBody
    explanation: str


class GetQuizResultResponseModel(BaseModel):
    status: str  # not started | started | finished
    score: int
    problems: list[GetQuizResultProblemModelBody]


class PatchQuizResultProblemModelBody(BaseModel):
    problem_num: int
    answer: AnswerModelBody


class PatchQuizResultRequestModel(BaseModel):
    status: str  # started | finished
    answers: list[PatchQuizResultProblemModelBody]


class PatchQuizResultAnswerModelBody(BaseModel):
    problem_num: int
    correct_answer: AnswerModelBody
    explanation: str


class PatchQuizResultResponseModel(BaseModel):
    answer_responses: list[PatchQuizResultAnswerModelBody]
