from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone_number = Column(String(20))
    email = Column(String(255))
    preferred_language = Column(String(10))
    created_at = Column(TIMESTAMP)
    password_hash = Column(String(255))

class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id"))
    feedback_text = Column(Text)
    translated_text = Column(Text)
    rating = Column(Integer)
    sentiment = Column(String(20))
    topic = Column(String(50), nullable=True)
    urgency = Column(String(10), nullable=True)
    language = Column(String(10))
    created_at = Column(TIMESTAMP)

class Reminder(Base):
    __tablename__ = "reminders"
    reminder_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.patient_id"))
    message = Column(Text)
    scheduled_time = Column(ARRAY(TIMESTAMP))
    days = Column(ARRAY(String(20)))
    status = Column(String(20))
    created_at = Column(TIMESTAMP)

class ReminderDelivery(Base):
    __tablename__ = "reminder_delivery"
    delivery_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey("reminders.reminder_id"))
    sent_at = Column(TIMESTAMP)
    delivery_status = Column(String(20))
    provider_response = Column(Text)
