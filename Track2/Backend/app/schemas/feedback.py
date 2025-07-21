# Pydantic: feedback
from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    user_id: int
    comments: str
    checklist: str

class FeedbackOut(BaseModel):
    id: int
    user_id: int
    comments: str
    checklist: str
