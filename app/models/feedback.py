from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel

class Feedback(RootModel):
    class Settings:
        name = "feedback"
        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING),
                ]
            )
        ]
    user_id: str
    content: str