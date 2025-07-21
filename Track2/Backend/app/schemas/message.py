# Pydantic: chatbot exchange
from pydantic import BaseModel

class MessageCreate(BaseModel):
    user_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    user_id: int
    content: str
    response: str
