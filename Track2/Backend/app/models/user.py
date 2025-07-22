# User metadata (for analytics/eval)
from sqlalchemy import Column, String, Integer
from app.db.database import Base

from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import TIMESTAMP, func

class User(Base):
    __tablename__ = 'users'
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(200))
    phone_number = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    preferred_language = Column(String(10), default="en")
    created_at = Column(TIMESTAMP, server_default=func.now())
    password_hash = Column(String(255))
