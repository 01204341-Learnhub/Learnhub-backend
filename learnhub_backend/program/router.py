from fastapi import APIRouter, Depends
from typing import Annotated

from ..dependencies import common_pagination_parameters
from .schemas import Programs_model
from .services import list_programs_response


router = APIRouter(
        prefix="/programs",
        tags=['program'],
        dependencies=[Depends(common_pagination_parameters)]
        )

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]

@router.get("/", status_code=200, response_model_exclude_none=True)
def list_programs(common_paginations: common_page_params) -> Programs_model:
        response_body = list_programs_response(common_paginations["skip"],common_paginations["limit"])
        return  response_body

@router.get("/progress", status_code=200, response_model_exclude_none=True)
def read_progress(common_paginations: common_page_params):
    response_body = list_progress_response(
    skip=common_paginations["skip"],
    limit=common_paginations["limit"],
    ) 
    return response_body

@router.get("/progress/courses", status_code=200, response_model_exclude_none=True)
def read_progress_courses(common_paginations: common_page_params):
    response_body = list_courses_response(
    skip=common_paginations["skip"],
    limit=common_paginations["limit"],
    ) 
    return response_body

@router.get("/progress/courses/{course-id}", status_code=200, response_model_exclude_none=True)
def read_progress_courses_id(course_id: str, common_paginations: common_page_params):
    response_body = list_courses_response(
    skip=common_paginations["skip"],
    limit=common_paginations["limit"],
    course_id=course_id,
    ) 
    return response_body

@router.get("/progress/courses/{course-id}/students", status_code=200, response_model_exclude_none=True)
def read_progress_courses_id_students(course_id: str, common_paginations: common_page_params):
    response_body = list_courses_students_response(
    skip=common_paginations["skip"],
    limit=common_paginations["limit"],
    course_id=course_id,
    ) 
    return response_body

@router.post("/progress/courses", status_code=200, response_model_exclude_none=True)
def add_progress_courses(common_paginations: common_page_params):
    response_body = add_course_response(
        courses_body=courses_body
    )
    if response_body == None:
        raise Exception.bad_request
    return response_body

 

@router.patch(
    "/courses/{course_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=dict,
)
def edit_course_chapter(chapter_id: str, chapter_to_edit: EditCourseChapterRequestModel):
    response_body = edit_course_response(chapter_id=chapter_id,chapter_to_edit=chapter_to_edit)
    if response_body.matched_count == 0:
        raise Exception.not_found
    elif response_body.modified_count == 0:
        return {"message": "OK but no change"}
    return  {"message": "OK"}
    

@router.delete(
    "/courses/{course_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=dict,
)
def delete_course_chapter(chapter_id: str):
    response_body = delete_course_response(chapter_id=chapter_id)
    if response_body.deleted_count == 0:
        raise Exception.not_found
    return {"message": "OK"}