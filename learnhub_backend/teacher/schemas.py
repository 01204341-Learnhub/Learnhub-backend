from typing import Optional, Union
from pydantic import BaseModel, HttpUrl


# TEACHERS
class ListTeachersModelBody(BaseModel):
    teacher_id: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl | None = None


class ListTeachersResponseModel(BaseModel):
    teachers: list[ListTeachersModelBody]


class PostTeacherRequestModel(BaseModel):
    uid: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl | None = None


class PostTeacherResponseModel(BaseModel):
    teacher_id: str


class GetTeacherResponseModel(BaseModel):
    uid: str
    teacher_id: str
    username: str
    fullname: str
    email: str
    profile_pic: HttpUrl | None


class PatchTeacherRequestModel(BaseModel):
    username: str | None
    fullname: str | None
    profile_pic: HttpUrl | None


# PAYMENT METHOD
class GetTeacherPaymentMethodResponseModel(BaseModel):
    payment_method_id: str
    name: str
    type: str
    card_number: str
    cvc: str
    expiration_date: str
    holder_fullname: str


class ListTeacherPaymentMethodsResponseModel(BaseModel):
    payment_methods: list[GetTeacherPaymentMethodResponseModel]


class PostTeacherPaymentMethodRequestModel(BaseModel):
    name: str
    type: str
    card_number: str
    cvc: str
    expiration_date: str
    holder_fullname: str


class PostTeacherPaymentMethodResponseModel(BaseModel):
    payment_method_id: str


class PatchTeacherPaymentMethodRequestModel(BaseModel):
    name: str | None = None
    type: str | None = None
    card_number: str | None = None
    cvc: str | None = None
    expiration_date: str | None = None
    holder_fullname: str | None = None
