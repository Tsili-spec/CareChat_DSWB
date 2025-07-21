# User messages, chatbot responses
from sqlalchemy import Column, Integer, String, Text
from app.db.database import Base

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    content = Column(Text)
    response = Column(Text)
