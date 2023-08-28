from pydantic import TypeAdapter

from .database import query_list_programs
from .schemas import Programs_model, Program_model


def list_programs_response(skip: int = 0, limit : int = 0) -> Programs_model:
        queried_programs = query_list_programs(skip, limit)
        ta = TypeAdapter(list[Program_model])
        response_body = Programs_model(programs=ta.validate_python(queried_programs))
        return response_body
