from pydantic import TypeAdapter

from .database import query_list_programs,query_list_course_chapters
from .schemas import Programs_model, Program_model,Chapter_model,Chapters_model


def list_programs_response(skip: int = 0, limit : int = 0) -> Programs_model:
        queried_programs = query_list_programs(skip, limit)
        ta = TypeAdapter(list[Program_model])
        response_body = Programs_model(programs=ta.validate_python(queried_programs))
        return response_body

def list_course_chapters_response(course_id: str = None,skip: int = 0, limit : int = 0) -> Programs_model:
        queried_chapters = query_list_course_chapters(course_id,skip, limit)
        print(queried_chapters)
        ta = TypeAdapter(list[Chapter_model])
        response_body = Chapters_model(chapters=ta.validate_python(queried_chapters))
        return response_body
