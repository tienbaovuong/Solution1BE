from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel, RootEnum
from app.models.user import UserRoleEnum

class ClassifierEnum(RootEnum):
    PartofAHorizontalPortScan = "PartofAHorizontalPortScan"
    DDoS = "DDoS"
    Attack = "Attack"
    CC = "C&C"
    Benign = "Benign"

class History(RootModel):
    class Settings:
        name = "history"
        indexes = [
            IndexModel(
                [
                    ("submitter_id", ASCENDING),
                ]
            )
        ]
    submitter_id: str #ID of the submitter
    submitter_role: UserRoleEnum
    timestamp: str
    detection: bool
    classifier: ClassifierEnum
    severity: float