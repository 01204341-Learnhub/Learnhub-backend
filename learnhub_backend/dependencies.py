from pydantic import BaseModel


def common_pagination_parameters(skip: int = 0, limit: int = 100):
    return {"skip": skip, "limit": limit}


class GenericOKResponse(BaseModel):
    detail: str = "OK"
