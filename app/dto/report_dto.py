from datetime import datetime
from pydantic import BaseModel

class ReportResponseData(BaseModel):
    timestamp: str
    detection: bool
    classifier: str
    severity: float
    created_at: datetime