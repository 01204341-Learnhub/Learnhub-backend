from fastapi import HTTPException


class Exception:
    bad_request = HTTPException(400, detail="Bad Request")
    unauthorized = HTTPException(401, detail="Unauthorized")
    forbidden = HTTPException(
        403, detail="Forbidden"
    )  # unlike unauthorized the client's identity is known.
    not_found = HTTPException(404, detail="Not Found")
    method_not_allowed = HTTPException(405, detail="Method Not Allowed")
    request_timeout = HTTPException(408, detail="Request Timeout")
    teapot = HTTPException(418, detail="I'm a teapot")
