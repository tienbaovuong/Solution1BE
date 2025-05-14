from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    content: str

class FeedbackResponseData(BaseModel):
    id: str
    content: str
    created_at: str
    updated_at: str
    user_id: str

