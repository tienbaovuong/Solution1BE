import logging
from datetime import datetime
from typing import Optional

from app.models.history import History
from app.dto.report_dto import ReportResponseData

_logger = logging.getLogger(__name__)

class ReportService:
    @staticmethod
    async def get_history_data(min_date: datetime, max_date: datetime, user_id: Optional[str]) -> list[ReportResponseData]:
        query = History.find(
            History.created_at >= min_date,
            History.created_at <= max_date
        )
        if user_id:
            query = query.find({"submitter_id": user_id})

        history_data = await query.project(ReportResponseData).to_list()
        return history_data