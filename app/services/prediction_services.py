import logging
from datetime import datetime
import asyncio
import io

import pandas as pd

from app.models.history import History, ClassifierEnum
from app.helpers.prediction import get_prediction
from app.dto.report_dto import ReportResponseData

_logger = logging.getLogger(__name__)

class PredictionService:
    @staticmethod
    async def save_prediction(
        list_of_prediction: list[History],
    ) -> list[ReportResponseData]:
        await History.insert_many(list_of_prediction)
        prediction_data = []
        for prediction in list_of_prediction:
            prediction_data.append(ReportResponseData(**prediction.model_dump()))
        return prediction_data
    
    @staticmethod
    async def get_prediction(file: bytes, user_id: str, role: str) -> list[ReportResponseData]:
        df = pd.read_csv(io.BytesIO(file), encoding='utf-8', sep="|")
        _logger.info(df.head())
        # try:
        prediction_df = get_prediction(df)
        # except Exception as e:
        #     _logger.error(f"Error in prediction: {e}")
        #     raise ValueError("File format is not correct")

        history_data = []
        for index, row in prediction_df.iterrows():
            history = History(
                submitter_id=user_id,
                submitter_role=role,
                detection=bool(row['detection']),
                classifier=ClassifierEnum[row['classifier']],
                severity=row['severity'],
                timestamp=str(row['timestamp']),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            history_data.append(history)

        prediction_data = await PredictionService.save_prediction(history_data)
        return prediction_data
    
    