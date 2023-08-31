from typing import Annotated, Union
from pydantic import TypeAdapter

from .database import query_list_programs,query_list_course_chapters,insert_course_chapter,find_course_chapter
from .schemas import List_course_chapters_chapter_model,List_course_chapters_chapters_model,Add_course_chapters_chapter_model
from .database import query_list_programs
from .schemas import ListProgramsModel, ListProgramsCourseModel, ListProgramsClassModel


def list_programs_response(skip: int = 0, limit : int = 0) -> ListProgramsModel:
        queried_programs = query_list_programs(skip, limit)
        ta = TypeAdapter(list[Union[ListProgramsClassModel, ListProgramsCourseModel]])
        response_body = ListProgramsModel(programs=ta.validate_python(queried_programs))
        return response_body

def list_course_chapters_response(course_id: str = None,skip: int = 0, limit : int = 0) -> Programs_model:
        queried_chapters = query_list_course_chapters(course_id=course_id,skip=skip, limit=limit)
        ta = TypeAdapter(list[List_course_chapters_chapter_model])
        response_body = List_course_chapters_chapters_model(chapters=ta.validate_python(queried_chapters))
        return response_body

def add_course_chapter_response(course_id:str , chapter_body:Add_course_chapters_chapter_model) -> dict:
        response = insert_course_chapter(course_id=course_id , chapter_body=chapter_body)
        return response

def get_course_chapter_response(chapter_id: str):
        queried_chapter = find_course_chapter(chapter_id=chapter_id)
        ta = TypeAdapter(List_course_chapters_chapter_model)
        response_body = List_course_chapters_chapter_model(**ta.validate_python(queried_chapter).model_dump())
        return response_body