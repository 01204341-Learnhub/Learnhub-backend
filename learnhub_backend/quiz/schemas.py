from datetime import datetime
from typing import Any
from pydantic import BaseModel, HttpUrl


class PlaceHolderModel(BaseModel):
    pass
# QUIZ
class ChoiceModelBody(BaseModel):
    choice_a: str
    choice_b: str
    choice_c: str
    choice_d: str
    choice_e: str
    choice_f: str

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


class AnswerModelBody(BaseModel):
    answer_a: bool
    answer_b: bool
    answer_c: bool
    answer_d: bool
    answer_e: bool
    answer_f: bool
class CorrectAnswerModelBody(BaseModel):
    answer_a: bool
    answer_b: bool
    answer_c: bool
    answer_d: bool
    answer_e: bool
    answer_f: bool
class GetQuizResultProblemModelBody(BaseModel):
    problem_num: int
    answer: AnswerModelBody
    correct_answer: CorrectAnswerModelBody
    explanation: str
class GetQuizResultResponseModel(BaseModel):
    status: str
    score: int
    problems: list[GetQuizResultProblemModelBody]