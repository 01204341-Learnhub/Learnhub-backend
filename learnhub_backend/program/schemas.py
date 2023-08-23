from typing import Optional
from pydantic import BaseModel

## Programs
class Program(BaseModel):
    course_id: Optional[str]
    class_id: Optional[str]
    type: str
    name: str

class Programs(BaseModel):
    programs: list[Program]
