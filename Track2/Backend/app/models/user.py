# User metadata (for analytics/eval)
from sqlalchemy import Column, String, Integer
from app.db.database import Base

from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import TIMESTAMP

class User(Base):
    __tablename__ = 'users'
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200))
    phone_number = Column(String(20))
    email = Column(String(255))
    preferred_language = Column(String(10))
    created_at = Column(TIMESTAMP)
    password_hash = Column(String(255))
