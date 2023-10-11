from fastapi import APIRouter, Depends
from typing import Annotated
from ..dependencies import (
    common_pagination_parameters,
    GenericOKResponse,
    Exception,
)

from .services import (
    delete_teacher_payment_method_request,
    get_teacher_payment_method_response,
    get_teacher_response,
    list_teacher_classes_response,
    list_teacher_courses_response,
    list_teacher_payment_methods_response,
    list_teachers_response,
    patch_teacher_payment_method_request,
    patch_teacher_request,
    post_teacher_payment_method_request,
    post_teacher_request,
)

from .schemas import (
    GetTeacherPaymentMethodResponseModel,
    GetTeacherResponseModel,
    ListTeacherClassesResponseModel,
    ListTeacherCoursesResponseModel,
    ListTeacherPaymentMethodsResponseModel,
    ListTeachersResponseModel,
    PatchTeacherPaymentMethodRequestModel,
    PatchTeacherRequestModel,
    PostTeacherPaymentMethodRequestModel,
    PostTeacherPaymentMethodResponseModel,
    PostTeacherRequestModel,
    PostTeacherResponseModel,
)

router = APIRouter(
    prefix="/users/teachers",
    tags=["teacher"],
    dependencies=[
        Depends(common_pagination_parameters),
        Depends(GenericOKResponse),
        Depends(Exception),
    ],
)

common_page_params = Annotated[dict, Depends(router.dependencies[0].dependency)]


@router.get(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListTeachersResponseModel,
)
def list_teachers(common_paginations: common_page_params):
    response_body = list_teachers_response(
        skip=common_paginations["skip"],
        limit=common_paginations["limit"],
    )
    return response_body


@router.post(
    "/",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostTeacherResponseModel,
)
def post_teacher(request_body: PostTeacherRequestModel):
    response_body = post_teacher_request(request_body)
    return response_body


@router.get(
    "/{teacher_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetTeacherResponseModel,
)
def get_teacher(teacher_id: str):
    response_body = get_teacher_response(teacher_id)
    return response_body


@router.patch(
    "/{teacher_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def patch_teacher(teacher_id: str, request_body: PatchTeacherRequestModel):
    response_body = patch_teacher_request(teacher_id, request_body)
    return response_body


@router.delete(
    "/{teacher_id}",
    status_code=200,
    response_model_exclude_none=True,
)
def delete_teacher(teacher_id: str):
    # TODO: Implement delete teacher
    return {"detail": "this endpoint is not currently supported"}


# PROGRAM
@router.get(
    "/{teacher_id}/courses",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListTeacherCoursesResponseModel,
)
def list_teacher_courses(teacher_id: str):
    response_body = list_teacher_courses_response(teacher_id)
    return response_body


@router.get(
    "/{teacher_id}/classes",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListTeacherClassesResponseModel,
)
def list_teacher_classes(teacher_id: str):
    response_body = list_teacher_classes_response(teacher_id)
    return response_body


# PAYMENT METHOD
@router.get(
    "/{teacher_id}/payment-methods",
    status_code=200,
    response_model_exclude_none=True,
    response_model=ListTeacherPaymentMethodsResponseModel,
)
def list_teacher_payment_method(teacher_id: str):
    response_body = list_teacher_payment_methods_response(teacher_id)
    return response_body


@router.post(
    "/{teacher_id}/payment-methods",
    status_code=200,
    response_model_exclude_none=True,
    response_model=PostTeacherPaymentMethodResponseModel,
)
def post_teacher_payment_method(
    teacher_id: str, request_body: PostTeacherPaymentMethodRequestModel
):
    response_body = post_teacher_payment_method_request(teacher_id, request_body)
    return response_body


@router.get(
    "/{teacher_id}/payment-methods/{payment_method_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GetTeacherPaymentMethodResponseModel,
)
def get_teacher_payment_method(teacher_id: str, payment_method_id: str):
    response_body = get_teacher_payment_method_response(teacher_id, payment_method_id)
    return response_body


@router.patch(
    "/{teacher_id}/payment-methods/{payment_method_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def patch_teacher_payment_method(
    teacher_id: str,
    payment_method_id: str,
    request_body: PatchTeacherPaymentMethodRequestModel,
):
    response_body = patch_teacher_payment_method_request(
        teacher_id, payment_method_id, request_body
    )
    return response_body


@router.delete(
    "/{teacher_id}/payment-methods/{payment_method_id}",
    status_code=200,
    response_model_exclude_none=True,
    response_model=GenericOKResponse,
)
def delete_teacher_payment_method(teacher_id: str, payment_method_id: str):
    response_body = delete_teacher_payment_method_request(teacher_id, payment_method_id)
    return response_body
