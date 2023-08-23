from typing import Optional
from pydantic import BaseModel

## Programs
class Program(BaseModel):
    course_id: Optional[str]
    class_id: Optional[str]
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

class Programs(BaseModel):
    programs: list[Program]
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
