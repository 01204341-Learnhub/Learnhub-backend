from typing import Optional, Union
from pydantic import BaseModel

## Programs
class ListProgramsClassModel(BaseModel):
    class_id: str 
    type: str
    name: str

    model_config =  {
            "json_schema_extra":{
                "examples":[
                    {
                        "class_id": "1234",
                        "type":"class",
                        "name":"Discreet Math"
                        }
                    ]
                }
            }

class ListProgramsCourseModel(BaseModel):
    course_id: str
    type: str
    name: str

    model_config =  {
            "json_schema_extra":{
                "examples":[
                    {
                        "course_id": "1234",
                        "type":"course",
                        "name":"Intro to Python"
                        }
                    ]
                }
            }

class Programs_model(BaseModel):
    programs: list[Program_model]
    model_config =  {
            "json_schema_extra":{
                "examples":[
                    {
                        "programs":[
                            {
                            "course_id": "1234",
                            "type":"course",
                            "name":"Discreet Math"
                                }
                            ]
                        }
                    ]
                }
            }
    
class List_course_chapters_chapter_model(BaseModel):
    chapter_id: str
    chapter_num: int
    name: str

class List_course_chapters_chapters_model(BaseModel):
    chapters: list[List_course_chapters_chapter_model]

class Add_course_chapters_chapter_model(BaseModel):
    chapter_num: int
    name: str
class ListProgramsModel(BaseModel):
    programs: list[Union[ListProgramsClassModel, ListProgramsCourseModel]]

