"""
Pydantic schemas for API request/response validation
Separate from database models for better separation of concerns
"""

# Base schemas
from .base import (
    BaseResponse, SuccessResponse, ErrorResponse, 
    PaginationParams, PaginatedResponse,
    EmergencyContact, UserLocation, PyObjectId
)

# Authentication schemas
from .auth import (
    UserRegistration, UserLogin, TokenResponse, 
    RefreshTokenRequest, PasswordChangeRequest,
    PasswordResetRequest, PasswordResetConfirm, LogoutResponse
)

# User schemas
from .user import (
    UserProfile, UserResponse, UserUpdateRequest,
    UserCreateRequest, UserSearchRequest, UserStatsResponse
)

# Conversation schemas
from .conversation import (
    MessageRole, MessageType, ConversationStatus,
    MessageContent, Message, ConversationCreateRequest,
    ConversationResponse, ConversationUpdateRequest,
    MessageCreateRequest, MessageResponse,
    ConversationSearchRequest, ConversationStatsResponse
)

# Feedback schemas
from .feedback import (
    FeedbackType, FeedbackStatus, SentimentType,
    FeedbackEntry, FeedbackSessionCreateRequest,
    FeedbackSessionResponse, FeedbackSessionUpdateRequest,
    FeedbackEntryCreateRequest, FeedbackSearchRequest,
    FeedbackStatsResponse
)

# Reminder schemas
from .reminder import (
    ReminderType, ReminderStatus, DeliveryMethod,
    RecurrencePattern, ReminderDeliveryStatus,
    ReminderSchedule, SmartReminderCreateRequest,
    SmartReminderResponse, SmartReminderUpdateRequest,
    ReminderDeliveryCreateRequest, ReminderDeliveryResponse,
    ReminderSearchRequest, ReminderStatsResponse
)

# Analytics schemas
from .analytics import (
    AnalyticsTimeframe, MetricType, EventType,
    SystemMetric, AnalyticsEventCreateRequest,
    AnalyticsEventResponse, MetricCreateRequest,
    AnalyticsQueryRequest, DashboardStatsResponse,
    UserEngagementResponse, SystemPerformanceResponse,
    AuditLogCreateRequest, AuditLogResponse
)
