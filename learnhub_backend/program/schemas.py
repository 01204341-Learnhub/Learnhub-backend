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

class ListProgramsModel(BaseModel):
    programs: list[Union[ListProgramsClassModel, ListProgramsCourseModel]]

