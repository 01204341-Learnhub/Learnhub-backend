from pydantic import BaseModel


## PURCHASE
class PostPurchaseRequestModel(BaseModel):
    student_id: str
    payment_method_id: str


class PostPurchaseResponseModel(BaseModel):
    transaction_id: str
