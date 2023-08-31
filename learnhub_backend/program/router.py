from fastapi import APIRouter, Depends
from typing import Annotated, Union

from ..dependencies import common_pagination_parameters
from .schemas import Programs_model,List_course_chapters_chapters_model,List_course_chapters_chapter_model,Add_course_chapters_chapter_model
from .services import list_programs_response,list_course_chapters_response,add_course_chapter_response,get_course_chapter_response
from .schemas import ListProgramsModel
from .services import list_programs_response


router = APIRouter(
        prefix="/programs",
        tags=['program'],
        dependencies=[Depends(common_pagination_parameters)]
        )

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]

@router.get("/", status_code=200, response_model=ListProgramsModel, response_model_exclude_none=True)
def list_programs(common_paginations: common_page_params) -> ListProgramsModel:
        response_body = list_programs_response(common_paginations["skip"],common_paginations["limit"])
        return  response_body

@router.get("/courses/{course_id}/chapters", status_code=200, response_model_exclude_none=True)
def list_course_chapters(course_id:str,common_paginations: common_page_params) -> List_course_chapters_chapters_model:
        response_body = list_course_chapters_response(skip=common_paginations["skip"],limit=common_paginations["limit"],course_id=course_id)
        return  response_body

@router.post("/courses/{course_id}/chapters", status_code=200, response_model_exclude_none=True)
def add_course_chapter(course_id: str ,chapter_body:Add_course_chapters_chapter_model):
        response_body = add_course_chapter_response(course_id=course_id,chapter_body=chapter_body)
        return  

@router.get("/courses/{course_id}/chapters/{chapter_id}", status_code=200, response_model_exclude_none=True)
def get_course_chapter(chapter_id:str):
        response_body=get_course_chapter_response(chapter_id=chapter_id)
        return response_body
