"""
Database models for MongoDB collections
These represent the actual data structure stored in the database
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
import uuid


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.is_instance_schema(cls),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


class MongoBaseModel(BaseModel):
    """Base model for MongoDB documents"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =====================================================
# EMBEDDED DOCUMENT MODELS
# =====================================================

class EmergencyContact(BaseModel):
    name: str = Field(..., max_length=200)
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    relationship: str = Field(..., max_length=100)


class UserLocation(BaseModel):
    city: str = Field(..., max_length=100)
    region: str = Field(..., max_length=100)
    country: str = Field(..., max_length=3)  # ISO country code
    timezone: str = Field(..., max_length=50)


class UserProfile(BaseModel):
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, pattern=r"^(M|F|Other|Prefer not to say)$")
    location: Optional[UserLocation] = None
    medical_conditions: Optional[List[str]] = None
    emergency_contact: Optional[EmergencyContact] = None


class QuietHours(BaseModel):
    enabled: bool = False
    start_time: str = Field("22:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    end_time: str = Field("07:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")


class UserPreferences(BaseModel):
    notification_methods: List[str] = Field(default=["sms"])
    quiet_hours: Optional[QuietHours] = None
    language_learning_reminders: bool = True
    health_tips_frequency: str = Field("daily", pattern=r"^(never|daily|weekly|monthly)$")
    ai_interaction_level: str = Field("intermediate", pattern=r"^(basic|intermediate|advanced)$")


class LoginHistory(BaseModel):
    timestamp: datetime
    ip_address: str
    user_agent: Optional[str] = None


class AccountStatus(BaseModel):
    is_active: bool = True
    is_verified: bool = False
    verification_method: Optional[str] = Field(None, pattern=r"^(phone|email|manual)$")
    last_login: Optional[datetime] = None
    failed_login_attempts: int = Field(0, ge=0)


class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4()}")
    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processed_by: Optional[str] = None  # AI model that processed this message


class FeedbackEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: f"entry_{uuid.uuid4()}")
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResponsePatterns(BaseModel):
    success_messages: List[str] = Field(default_factory=list)
    confirmation_phrases: List[str] = Field(default_factory=list)
    escalation_triggers: List[str] = Field(default_factory=list)


class ReminderSchedule(BaseModel):
    pattern: str = Field(..., pattern=r"^(once|daily|weekly|monthly|custom)$")
    start_date: datetime
    end_date: Optional[datetime] = None
    time_of_day: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    days_of_week: Optional[List[int]] = Field(None, description="0=Monday, 6=Sunday")
    interval_days: Optional[int] = None


# =====================================================
# MAIN COLLECTION MODELS
# =====================================================

class User(MongoBaseModel):
    """User collection model"""
    user_id: str = Field(default_factory=lambda: f"usr_{uuid.uuid4()}")
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    full_name: str = Field(..., min_length=2, max_length=200)
    hashed_password: str = Field(..., min_length=60)
    preferred_language: str = Field("fr", pattern=r"^(en|fr|ar|es|pt)$")
    
    profile: UserProfile = Field(default_factory=UserProfile)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    account_status: AccountStatus = Field(default_factory=AccountStatus)
    login_history: List[LoginHistory] = Field(default_factory=list)


class Conversation(MongoBaseModel):
    """Conversation collection model"""
    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4()}")
    user_id: str = Field(..., description="User who owns this conversation")
    title: Optional[str] = Field(None, max_length=200)
    status: str = Field("active", pattern=r"^(active|paused|completed|archived)$")
    messages: List[Message] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    ai_summary: Optional[str] = None
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class FeedbackSession(MongoBaseModel):
    """Feedback session collection model"""
    session_id: str = Field(default_factory=lambda: f"feedback_{uuid.uuid4()}")
    user_id: str = Field(..., description="User who provided feedback")
    conversation_id: Optional[str] = Field(None, description="Related conversation")
    feedback_type: str = Field("general", pattern=r"^(satisfaction|complaint|suggestion|bug_report|feature_request|general)$")
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: str = Field("pending", pattern=r"^(pending|in_review|resolved|closed)$")
    
    entries: List[FeedbackEntry] = Field(default_factory=list)
    sentiment_analysis: Optional[str] = Field(None, pattern=r"^(positive|negative|neutral)$")
    average_rating: Optional[float] = None
    priority: int = Field(1, ge=1, le=5)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    response_from_admin: Optional[str] = None
    resolved_at: Optional[datetime] = None


class SmartReminder(MongoBaseModel):
    """Smart reminder collection model"""
    reminder_id: str = Field(default_factory=lambda: f"reminder_{uuid.uuid4()}")
    user_id: str = Field(..., description="User who owns this reminder")
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=1000)
    reminder_type: str = Field("custom", pattern=r"^(medication|appointment|health_check|exercise|diet|custom)$")
    status: str = Field("active", pattern=r"^(active|paused|completed|cancelled)$")
    
    schedule: ReminderSchedule
    delivery_methods: List[str] = Field(..., min_items=1)
    priority: int = Field(1, ge=1, le=5)
    
    next_delivery: Optional[datetime] = None
    total_deliveries: int = Field(0, ge=0)
    successful_deliveries: int = Field(0, ge=0)
    last_delivery: Optional[datetime] = None
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
    response_patterns: Optional[ResponsePatterns] = None


class ReminderDelivery(MongoBaseModel):
    """Reminder delivery collection model"""
    delivery_id: str = Field(default_factory=lambda: f"delivery_{uuid.uuid4()}")
    reminder_id: str = Field(..., description="Parent reminder")
    user_id: str = Field(..., description="Target user")
    
    scheduled_for: datetime
    delivered_at: Optional[datetime] = None
    delivery_method: str = Field(..., pattern=r"^(sms|email|push_notification|voice_call)$")
    recipient: str = Field(..., description="Phone number or email")
    
    status: str = Field("pending", pattern=r"^(pending|sent|delivered|failed|acknowledged)$")
    message_content: str = Field(..., max_length=1000)
    
    response_received: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = Field(0, ge=0)


class NotificationTemplate(MongoBaseModel):
    """Notification template collection model"""
    template_id: str = Field(default_factory=lambda: f"template_{uuid.uuid4()}")
    name: str = Field(..., max_length=100)
    type: str = Field(..., pattern=r"^(reminder|feedback|system|marketing)$")
    delivery_method: str = Field(..., pattern=r"^(sms|email|push_notification|voice_call)$")
    
    subject: Optional[str] = Field(None, max_length=200)  # For email
    body_template: str = Field(..., max_length=2000)
    variables: List[str] = Field(default_factory=list)  # Available variables
    
    language: str = Field("en", pattern=r"^(en|fr|ar|es|pt)$")
    is_active: bool = True
    
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SystemAnalytics(MongoBaseModel):
    """System analytics collection model"""
    event_id: str = Field(default_factory=lambda: f"event_{uuid.uuid4()}")
    event_type: str = Field(..., max_length=100)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    event_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


class SystemAuditLog(MongoBaseModel):
    """System audit log collection model"""
    log_id: str = Field(default_factory=lambda: f"audit_{uuid.uuid4()}")
    action: str = Field(..., max_length=100)
    resource_type: str = Field(..., max_length=50)
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    changes: Dict[str, Any] = Field(default_factory=dict)  # Before/after changes
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: str = Field("info", pattern=r"^(debug|info|warning|error|critical)$")
