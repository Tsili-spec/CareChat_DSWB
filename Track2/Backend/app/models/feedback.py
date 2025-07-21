# Feedback, evaluation checklists
from sqlalchemy import Column, Integer, String, Text
from app.db.database import Base

class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    comments = Column(Text)
    checklist = Column(Text)
