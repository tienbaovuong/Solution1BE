from fastapi import APIRouter, Depends, Query

from app.dto.common import BasePaginationResponseData, BaseResponseData
from app.dto.feedback_dto import FeedbackRequest
from app.models.user import UserRoleEnum
from app.services.feedback_services import FeedbackService
from app.helpers.auth_helpers import get_current_user

router = APIRouter(tags=['Feedback'], prefix="/feedback")

@router.get(
    "/list_feedbacks",
    response_model=BasePaginationResponseData,
)
async def list_feedbacks(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    if role != UserRoleEnum.ADMIN:
        return BasePaginationResponseData(
            code=403,
            message="Permission denied",
            data=None
        )
    feedbacks, total = await FeedbackService.get_list_feedbacks(page, size)
    return BasePaginationResponseData(
        data=feedbacks,
        total=total,
        page=page,
        size=size
    )

@router.get(
    "/list_feedback_by_self",
    response_model=BasePaginationResponseData,
)
async def list_feedback_by_self(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    feedbacks, total = await FeedbackService.get_feedback_by_user_id(user_id, page, size)
    return BasePaginationResponseData(
        data=feedbacks,
        total=total,
        page=page,
        size=size
    )

@router.get(
    "/{feedback_id}",
    response_model=BaseResponseData,
)
async def get_feedback_by_id(
    feedback_id: str,
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    if role != UserRoleEnum.ADMIN:
        return BaseResponseData(
            code=403,
            message="Permission denied",
            data=None
        )
    feedback = await FeedbackService.get_feedback_by_id(feedback_id)
    return BaseResponseData(
        message="Succeed",
        data=feedback
    )

@router.post(
    "/create_feedback",
    response_model=BaseResponseData,
)
async def create_feedback(
    request: FeedbackRequest,
    current_user: str = Depends(get_current_user),
):
    user_id, role = current_user
    feedback = await FeedbackService.create_feedback(user_id, request)
    return BaseResponseData(
        message="Succeed",
        data=feedback
    )