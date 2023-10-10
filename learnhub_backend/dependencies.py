from pydantic import BaseModel
from fastapi import HTTPException
import mimetypes
import httpx


def common_pagination_parameters(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}


class GenericOKResponse(BaseModel):
    detail: str = "OK"


class Exception:
    # 4xx
    bad_request = HTTPException(400, detail="Bad Request")
    unauthorized = HTTPException(401, detail="Unauthorized")
    forbidden = HTTPException(
        403, detail="Forbidden"
    )  # unlike unauthorized the client's identity is known.
    not_found = HTTPException(404, detail="Not Found")
    method_not_allowed = HTTPException(405, detail="Method Not Allowed")
    request_timeout = HTTPException(408, detail="Request Timeout")
    unprocessable_content = HTTPException(422, detail="Unprocessable Content")

    # 5xx
    internal_server_error = HTTPException(500, detail="Internal Server Error")

    # MEME
    teapot = HTTPException(418, detail="I'm a teapot")


# TYPE
student_type = "student"
teacher_type = "teacher"
course_type = "course"
class_type = "class"


# FIX: Doesn't work for youtube video
def CheckHttpFileType(url: str) -> str:
    result = mimetypes.guess_type(url)[0]  # ('audio/mpeg', None)
    if result == None:  # no extension url
        # download only 'Content-Type' metadata
        response = httpx.head(url).headers[
            "Content-Type"
        ]  # ex. 'texts/html; charset=utf-8' or 'application/pdf'
        result = response.split(";")[0]
    file_type, extension = result.split("/")  # 'video/mp4'
    return file_type
