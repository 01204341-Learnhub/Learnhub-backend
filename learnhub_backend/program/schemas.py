from typing import Optional, Union
from pydantic import BaseModel

## Programs
class List_programs_class_model(BaseModel):
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

class List_programs_course_model(BaseModel):
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

class List_programs_model(BaseModel):
    programs: list[Union[List_programs_course_model, List_programs_class_model]]

