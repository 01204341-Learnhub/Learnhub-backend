from typing import Optional, Union
from pydantic import BaseModel, HttpUrl, validator


## COURSE PURCHASE
class PostCoursePurchaseRequestModel(BaseModel):
    student_id: str
    payment_method_id: str


class PostCoursePurchaseResponseModel(BaseModel):
    transaction_id: str
