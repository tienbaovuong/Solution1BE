import logging
from datetime import datetime
from beanie import PydanticObjectId

from app.dto.feedback_dto import FeedbackResponseData, FeedbackRequest
from app.models.feedback import Feedback
from app.helpers.exceptions import NotFoundException

_logger = logging.getLogger(__name__)

class FeedbackService:
    @staticmethod
    async def get_list_feedbacks(page: int, size: int) -> tuple[list[FeedbackResponseData], int]:
        skip = (page - 1) * size
        feedbacks = await Feedback.find_all().sort(-Feedback.created_at).skip(skip).limit(size).project(FeedbackResponseData).to_list()
        total = await Feedback.count()
        return feedbacks, total
    
    @staticmethod
    async def get_feedback_by_id(feedback_id: str) -> FeedbackResponseData:
        feedback = await Feedback.get(PydanticObjectId(feedback_id))
        if not feedback:
            raise NotFoundException("Feedback not found")
        return feedback
    
    @staticmethod
    async def create_feedback(user_id: str, request: FeedbackRequest) -> FeedbackResponseData:
        feedback = Feedback(
            user_id=user_id,
            content=request.content,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await feedback.create()
        feedback_dto = FeedbackResponseData(
            id=str(feedback.id),
            content=feedback.content,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
            user_id=feedback.user_id
        )
        return feedback_dto
    
    @staticmethod
    async def get_feedback_by_user_id(user_id: str, page: int, size: int) -> tuple[list[FeedbackResponseData], int]:
        skip = (page - 1) * size
        feedbacks = await Feedback.find(Feedback.user_id == user_id).sort(-Feedback.created_at).skip(skip).limit(size).project(FeedbackResponseData).to_list()
        total = await Feedback.count(Feedback.user_id == user_id)
        return feedbacks, total