from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
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
# USER MODELS
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
    quiet_hours: QuietHours = Field(default_factory=QuietHours)
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


class User(MongoBaseModel):
    user_id: str = Field(default_factory=lambda: f"usr_{uuid.uuid4()}")
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    full_name: str = Field(..., min_length=2, max_length=200)
    hashed_password: str = Field(..., min_length=60)
    preferred_language: str = Field("fr", pattern=r"^(en|fr|ar|es|pt)$")
    
    profile: UserProfile = Field(default_factory=UserProfile)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    account_status: AccountStatus = Field(default_factory=AccountStatus)
    login_history: List[LoginHistory] = Field(default=[])

    class Config:
        schema_extra = {
            "example": {
                "user_id": "usr_123e4567-e89b-12d3-a456-426614174000",
                "phone_number": "+237123456789",
                "email": "patient@example.com",
                "full_name": "Marie Ngozi",
                "preferred_language": "fr",
                "profile": {
                    "date_of_birth": "1985-03-15T00:00:00Z",
                    "gender": "F",
                    "location": {
                        "city": "Buea",
                        "region": "South-West",
                        "country": "CM",
                        "timezone": "Africa/Douala"
                    },
                    "medical_conditions": ["hypertension", "diabetes_type_2"],
                    "emergency_contact": {
                        "name": "Jean Ngozi",
                        "phone": "+237987654321",
                        "relationship": "spouse"
                    }
                }
            }
        }


# =====================================================
# CONVERSATION MODELS
# =====================================================

class Translation(BaseModel):
    original_language: str
    translated_content: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class Entity(BaseModel):
    entity_type: str
    entity_value: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class SuggestedAction(BaseModel):
    action_type: str
    description: str
    priority: str = Field(..., pattern=r"^(low|medium|high|urgent)$")
    automated: bool = False


class AIAnalysis(BaseModel):
    sentiment: str = Field(..., pattern=r"^(very_positive|positive|neutral|negative|very_negative)$")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    intent: Optional[str] = None
    entities: List[Entity] = Field(default=[])
    urgency_level: str = Field(..., pattern=r"^(low|medium|high|critical)$")
    topics: List[str] = Field(default=[])
    suggested_actions: List[SuggestedAction] = Field(default=[])


class AIModelInfo(BaseModel):
    ai_model_name: str
    ai_model_version: str
    token_count: int = Field(..., ge=0)
    processing_time_ms: int = Field(..., ge=0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class Attachment(BaseModel):
    file_id: str
    file_name: str
    file_type: str
    file_size: int = Field(..., ge=0)
    file_url: str


class Message(BaseModel):
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4()}")
    role: str = Field(..., pattern=r"^(user|assistant|system|support_agent)$")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: str = Field("text", pattern=r"^(text|image|audio|file|quick_reply|feedback_response)$")
    language: str = "fr"
    
    translation: Optional[Translation] = None
    ai_analysis: Optional[AIAnalysis] = None
    ai_model_info: Optional[AIModelInfo] = None
    attachments: Optional[List[Attachment]] = None


class ConversationMetadata(BaseModel):
    title: str = Field(..., max_length=200)
    conversation_type: str = Field(..., pattern=r"^(general_chat|feedback_session|reminder_setup|medical_inquiry|support_request)$")
    language: str = "fr"
    status: str = Field("active", pattern=r"^(active|completed|archived|flagged)$")
    priority: str = Field("medium", pattern=r"^(low|medium|high|urgent)$")
    department: Optional[str] = None
    ai_model_used: str = "gemini-2.0-pro"
    total_messages: int = Field(0, ge=0)
    total_tokens_used: int = Field(0, ge=0)


class ConversationSummary(BaseModel):
    key_topics: List[str] = Field(default=[])
    patient_concerns: List[str] = Field(default=[])
    ai_recommendations: List[str] = Field(default=[])
    follow_up_required: bool = False
    next_follow_up_date: Optional[datetime] = None
    overall_sentiment: str = "neutral"
    satisfaction_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    resolution_status: str = Field("unresolved", pattern=r"^(resolved|partially_resolved|unresolved|escalated)$")


class Conversation(MongoBaseModel):
    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4()}")
    user_id: str
    metadata: ConversationMetadata
    messages: List[Message] = Field(default=[])
    conversation_summary: Optional[ConversationSummary] = None
    closed_at: Optional[datetime] = None


# =====================================================
# FEEDBACK SESSION MODELS
# =====================================================

class FeedbackSessionInfo(BaseModel):
    session_type: str = Field(..., pattern=r"^(post_visit|medication_feedback|service_quality|app_experience|general_feedback)$")
    language: str = "fr"
    status: str = Field("started", pattern=r"^(started|in_progress|completed|abandoned|expired)$")
    department: Optional[str] = None
    visit_date: Optional[datetime] = None
    visit_type: Optional[str] = None
    completion_percentage: float = Field(0.0, ge=0.0, le=100.0)
    estimated_duration_minutes: int = Field(5, ge=1)
    actual_duration_minutes: Optional[int] = None


class FeedbackAIAnalysis(BaseModel):
    sentiment: str = Field(..., pattern=r"^(very_positive|positive|neutral|negative|very_negative)$")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    key_topics: List[str] = Field(default=[])
    positive_aspects: List[str] = Field(default=[])
    negative_aspects: List[str] = Field(default=[])
    urgency_level: str = Field("low", pattern=r"^(low|medium|high|critical)$")
    requires_follow_up: bool = False
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    suggested_action: Optional[str] = None
    actionable_suggestion: bool = False


class FeedbackEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    feedback_type: str = Field(..., pattern=r"^(rating|text|choice|boolean|scale)$")
    question: Optional[str] = None
    response_value: Union[str, int, float, bool] = Field(...)
    response_text: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    sentiment: Optional[str] = Field(None, pattern=r"^(positive|neutral|negative)$")
    tags: List[str] = Field(default=[])
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackResponse(BaseModel):
    question: str
    question_en: Optional[str] = None
    response_type: str = Field(..., pattern=r"^(text|rating|choice|boolean)$")
    rating: Optional[int] = Field(None, ge=1, le=5)
    scale: Optional[str] = "1-5"
    selected_option: Optional[str] = None
    options: Optional[List[str]] = None
    original_text: Optional[str] = None
    translated_text: Optional[str] = None
    original_language: str = "fr"
    ai_analysis: Optional[FeedbackAIAnalysis] = None
    weight: float = Field(1.0, ge=0.1, le=5.0)


class SentimentBreakdown(BaseModel):
    positive_responses: int = Field(0, ge=0)
    neutral_responses: int = Field(0, ge=0)
    negative_responses: int = Field(0, ge=0)
    average_sentiment_score: float = Field(0.0, ge=-1.0, le=1.0)


class KeyTheme(BaseModel):
    theme: str
    frequency: int = Field(..., ge=1)
    sentiment: str = Field(..., pattern=r"^(positive|neutral|negative)$")


class UrgencyFlag(BaseModel):
    issue: str
    urgency_level: str = Field(..., pattern=r"^(low|medium|high|critical)$")
    requires_follow_up: bool = False


class FeedbackAnalytics(BaseModel):
    overall_satisfaction_score: Optional[float] = Field(None, ge=0.0, le=5.0)
    sentiment_breakdown: SentimentBreakdown = Field(default_factory=SentimentBreakdown)
    key_themes: List[KeyTheme] = Field(default=[])
    improvement_areas: List[str] = Field(default=[])
    positive_highlights: List[str] = Field(default=[])
    urgency_flags: List[UrgencyFlag] = Field(default=[])


class FeedbackSession(MongoBaseModel):
    session_id: str = Field(default_factory=lambda: f"fb_{uuid.uuid4()}")
    user_id: str
    session_info: FeedbackSessionInfo
    feedback_responses: Dict[str, FeedbackResponse] = Field(default={})
    analytics: FeedbackAnalytics = Field(default_factory=FeedbackAnalytics)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# =====================================================
# SMART REMINDER MODELS
# =====================================================

class ReminderConfig(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    type: str = Field(..., pattern=r"^(medication|appointment|exercise|diet|follow_up|test_reminder|custom)$")
    status: str = Field("active", pattern=r"^(active|paused|completed|cancelled|expired)$")
    priority: str = Field("medium", pattern=r"^(low|medium|high|critical)$")
    category: Optional[str] = None
    created_from: str = Field("manual", pattern=r"^(manual|chat_conversation|doctor_prescription|app_suggestion|imported)$")


class SchedulePattern(BaseModel):
    pattern_type: str = Field(..., pattern=r"^(daily|weekly|monthly|specific_dates|interval)$")
    times: List[str] = Field(..., min_items=1)  # Format: "HH:MM"
    days_of_week: Optional[List[str]] = Field(None)
    specific_dates: Optional[List[datetime]] = None
    interval_hours: Optional[int] = Field(None, ge=1)
    start_date: datetime
    end_date: Optional[datetime] = None
    timezone: str = "Africa/Douala"


class SchedulePreferences(BaseModel):
    preferred_methods: List[str] = Field(default=["sms"])
    backup_method: Optional[str] = None
    snooze_allowed: bool = True
    max_snooze_duration_minutes: int = Field(30, ge=5, le=120)
    escalation_enabled: bool = False
    escalation_after_minutes: Optional[int] = Field(None, ge=15)


class ReminderSchedule(BaseModel):
    patterns: List[SchedulePattern] = Field(..., min_items=1)
    preferences: SchedulePreferences = Field(default_factory=SchedulePreferences)


class QuickAction(BaseModel):
    action_id: str
    label: str
    label_translations: Dict[str, str] = Field(default={})
    action_type: str = Field(..., pattern=r"^(mark_completed|snooze|skip|reschedule|custom)$")
    parameters: Optional[Dict[str, Any]] = None


class EducationalLink(BaseModel):
    title: str
    url: str
    description: str


class RichContent(BaseModel):
    images: Optional[List[str]] = None  # URLs
    videos: Optional[List[str]] = None  # URLs
    educational_links: Optional[List[EducationalLink]] = None


class ReminderContent(BaseModel):
    message_templates: Dict[str, Dict[str, str]] = Field(default={})  # {language: {type: message}}
    quick_actions: List[QuickAction] = Field(default=[])
    rich_content: Optional[RichContent] = None


class DeliveryTracking(BaseModel):
    total_scheduled: int = Field(0, ge=0)
    total_sent: int = Field(0, ge=0)
    total_delivered: int = Field(0, ge=0)
    total_responded: int = Field(0, ge=0)
    last_delivery_attempt: Optional[datetime] = None
    next_scheduled_delivery: Optional[datetime] = None
    delivery_success_rate: float = Field(0.0, ge=0.0, le=1.0)


class ResponsePatterns(BaseModel):
    best_response_times: List[str] = Field(default=[])
    avg_response_time_minutes: float = Field(0.0, ge=0.0)
    preferred_response_method: str = "sms"
    consistency_score: float = Field(0.0, ge=0.0, le=1.0)


class OptimizationSuggestion(BaseModel):
    suggestion_type: str
    description: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    potential_improvement: str


class RiskAssessment(BaseModel):
    adherence_risk_level: str = Field("low", pattern=r"^(low|medium|high|critical)$")
    risk_factors: List[str] = Field(default=[])
    recommended_interventions: List[str] = Field(default=[])


class SmartInsights(BaseModel):
    adherence_rate: float = Field(0.0, ge=0.0, le=1.0)
    response_patterns: ResponsePatterns = Field(default_factory=ResponsePatterns)
    optimization_suggestions: List[OptimizationSuggestion] = Field(default=[])
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)


class SmartReminder(MongoBaseModel):
    reminder_id: str = Field(default_factory=lambda: f"rem_{uuid.uuid4()}")
    user_id: str
    reminder_config: ReminderConfig
    schedule: ReminderSchedule
    content: ReminderContent = Field(default_factory=ReminderContent)
    delivery_tracking: DeliveryTracking = Field(default_factory=DeliveryTracking)
    smart_insights: Optional[SmartInsights] = None
    last_triggered_at: Optional[datetime] = None


# =====================================================
# REMINDER DELIVERY MODELS
# =====================================================

class ErrorDetails(BaseModel):
    error_code: str
    error_message: str
    is_retryable: bool = True


class DeliveryInfo(BaseModel):
    method: str = Field(..., pattern=r"^(sms|whatsapp|email|push|voice_call)$")
    status: str = Field("pending", pattern=r"^(pending|sent|delivered|failed|cancelled)$")
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    provider: Optional[str] = None
    provider_message_id: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None
    error_details: Optional[ErrorDetails] = None
    retry_count: int = Field(0, ge=0)
    cost_usd: Optional[float] = Field(None, ge=0.0)


class ContentSent(BaseModel):
    message: str
    language: str = "fr"
    template_used: str
    personalization_data: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    responded_at: datetime
    response_method: str
    action_taken: str = Field(..., pattern=r"^(mark_completed|snooze|skip|reschedule|no_action)$")
    response_data: Optional[Dict[str, Any]] = None
    response_time_minutes: float = Field(..., ge=0.0)
    additional_notes: Optional[str] = None


class ReminderDelivery(MongoBaseModel):
    delivery_id: str = Field(default_factory=lambda: f"del_{uuid.uuid4()}")
    reminder_id: str
    user_id: str
    scheduled_time: datetime
    delivery_info: DeliveryInfo
    content_sent: ContentSent
    user_response: Optional[UserResponse] = None


class NotificationTemplate(MongoBaseModel):
    template_id: str = Field(default_factory=lambda: f"tmpl_{uuid.uuid4()}")
    template_type: str = Field(..., pattern=r"^(sms|email|whatsapp|push|voice)$")
    name: str = Field(..., max_length=200)
    subject: Optional[str] = Field(None, max_length=500)
    content: str = Field(..., max_length=2000)
    variables: List[str] = Field(default=[])
    language: str = Field("fr", pattern=r"^(en|fr|ar|es|pt)$")
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None


# =====================================================
# REQUEST/RESPONSE MODELS FOR API
# =====================================================

class UserCreateRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    full_name: str = Field(..., min_length=2, max_length=200)
    password: str = Field(..., min_length=8)
    preferred_language: str = Field("fr", pattern=r"^(en|fr|ar|es|pt)$")
    profile: Optional[UserProfile] = None
    preferences: Optional[UserPreferences] = None


class UserResponse(BaseModel):
    user_id: str
    phone_number: str
    email: Optional[str]
    full_name: str
    preferred_language: str
    account_status: AccountStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreateRequest(BaseModel):
    title: str = Field(..., max_length=200)
    conversation_type: str = Field(..., pattern=r"^(general_chat|feedback_session|reminder_setup|medical_inquiry|support_request)$")
    department: Optional[str] = None
    language: str = "fr"


class MessageCreateRequest(BaseModel):
    content: str
    message_type: str = Field("text", pattern=r"^(text|image|audio|file|quick_reply|feedback_response)$")
    language: str = "fr"


class FeedbackSessionCreateRequest(BaseModel):
    session_type: str = Field(..., pattern=r"^(post_visit|medication_feedback|service_quality|app_experience|general_feedback)$")
    department: Optional[str] = None
    visit_date: Optional[datetime] = None
    visit_type: Optional[str] = None
    language: str = "fr"


class ReminderCreateRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    type: str = Field(..., pattern=r"^(medication|appointment|exercise|diet|follow_up|test_reminder|custom)$")
    priority: str = Field("medium", pattern=r"^(low|medium|high|critical)$")
    category: Optional[str] = None
    schedule: ReminderSchedule
    content: Optional[ReminderContent] = None


# =====================================================
# UPDATE REQUEST MODELS
# =====================================================

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    preferred_language: Optional[str] = Field(None, pattern=r"^(en|fr|ar|es|pt)$")
    profile: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None


class ConversationUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, pattern=r"^(active|completed|archived|flagged)$")
    metadata: Optional[Dict[str, Any]] = None


class FeedbackSessionUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, pattern=r"^(started|in_progress|completed|abandoned|expired)$")
    metadata: Optional[Dict[str, Any]] = None


class SmartReminderUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, max_length=1000)
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern=r"^(active|paused|completed|cancelled)$")
    priority_level: Optional[str] = Field(None, pattern=r"^(low|medium|high|critical)$")
    delivery_channels: Optional[List[str]] = None
    recurrence_pattern: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# =====================================================
# ADD REQUEST MODELS
# =====================================================

class MessageAddRequest(BaseModel):
    sender_type: str = Field(..., pattern=r"^(user|assistant|system|support_agent)$")
    content: str = Field(..., max_length=10000)
    content_type: str = Field("text", pattern=r"^(text|image|audio|file|quick_reply|feedback_response)$")
    metadata: Optional[Dict[str, Any]] = None


class SmartReminderCreateRequest(BaseModel):
    reminder_type: str = Field(..., pattern=r"^(medication|appointment|exercise|diet|follow_up|test_reminder|custom)$")
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=1000)
    scheduled_time: datetime
    recurrence_pattern: Optional[Dict[str, Any]] = None
    priority_level: str = Field("medium", pattern=r"^(low|medium|high|critical)$")
    delivery_channels: List[str] = Field(default=["sms"])
    conditions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class FeedbackSessionCreateRequest(BaseModel):
    session_type: str = Field(..., pattern=r"^(post_visit|medication_feedback|service_quality|app_experience|general_feedback)$")
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# =====================================================
# RESPONSE MODELS
# =====================================================

class UserResponse(BaseModel):
    user_id: str
    phone_number: str
    email: Optional[str] = None
    full_name: str
    preferred_language: str
    account_status: AccountStatus
    created_at: datetime


class ConversationResponse(BaseModel):
    conversation_id: str
    user_id: str
    conversation_type: str
    status: str
    metadata: Dict[str, Any]
    message_count: int
    created_at: datetime
    updated_at: datetime


class FeedbackSessionResponse(BaseModel):
    session_id: str
    user_id: str
    session_type: str
    conversation_id: Optional[str] = None
    status: str
    metadata: Dict[str, Any]
    feedback_count: int
    created_at: datetime
    updated_at: datetime


class SmartReminderResponse(BaseModel):
    reminder_id: str
    user_id: str
    reminder_type: str
    title: str
    scheduled_time: datetime
    status: str
    priority_level: str
    delivery_channels: List[str]
    created_at: datetime
    updated_at: datetime
