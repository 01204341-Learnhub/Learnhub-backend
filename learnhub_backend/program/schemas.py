from typing import Optional
from pydantic import BaseModel

## Programs
class Program_model(BaseModel):
    course_id: str | None=None
    class_id: str | None=None
    type: str
    name: str

    model_config =  {
            "json_schema_extra":{
                "examples":[
                    {
                        "course_id": "1234",
                        "type":"course",
                        "name":"Discreet Math"
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
