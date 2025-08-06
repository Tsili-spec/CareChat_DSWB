from beanie import Document, Indexed
from pydantic import Field, EmailStr
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
import uuid

from beanie import Document, Indexed
from pydantic import Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
import uuid

class Patient(Document):
    """Patient model for MongoDB using Beanie ODM"""
    
    patient_id: Optional[str] = Field(default=None, alias="_id")
    full_name: str = Field(..., min_length=1, max_length=200)
    phone_number: str = Field(..., min_length=8, max_length=20)  # Will be indexed in Settings
    email: Optional[EmailStr] = None
    preferred_language: str = Field(default="en", max_length=10)
    password_hash: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('patient_id', mode='before')
    @classmethod
    def validate_patient_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v or str(uuid.uuid4())
    
    class Settings:
        name = "patients"  # MongoDB collection name
        indexes = [
            "phone_number",  # Index for login queries
            "email",         # Index for email queries
            "created_at"     # Index for date queries
        ]

class Feedback(Document):
    """Feedback model for MongoDB using Beanie ODM"""
    
    patient_id: str = Field(...)
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback_text: Optional[str] = None
    translated_text: Optional[str] = None
    language: str = Field(...)
    sentiment: Optional[str] = None
    topic: Optional[str] = None
    urgency: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "feedback"
        indexes = [
            "patient_id",
            "sentiment",
            "topic",
            "urgency",
            "created_at"
        ]

class Reminder(Document):
    """Reminder model for MongoDB using Beanie ODM"""
    
    patient_id: str = Field(...)
    title: str = Field(..., max_length=200)
    message: str = Field(...)
    scheduled_time: List[datetime] = Field(default_factory=list)
    days: List[str] = Field(default_factory=list)
    status: str = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "reminders"
        indexes = [
            "patient_id",
            "status",
            "scheduled_time",
            "created_at"
        ]

class ReminderDelivery(Document):
    """Reminder delivery tracking model for MongoDB using Beanie ODM"""
    
    reminder_id: str = Field(...)
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    delivery_status: str = Field(...)
    provider_response: Optional[str] = None
    
    class Settings:
        name = "reminder_delivery"
        indexes = [
            "reminder_id",
            "delivery_status",
            "sent_at"
        ]
