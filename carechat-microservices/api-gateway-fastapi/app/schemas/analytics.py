"""
Analytics schemas for system monitoring and reporting
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from .base import BaseResponse


class AnalyticsTimeframe(str, Enum):
    """Analytics timeframe enumeration"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class MetricType(str, Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class EventType(str, Enum):
    """System event type enumeration"""
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    CONVERSATION_STARTED = "conversation_started"
    MESSAGE_SENT = "message_sent"
    FEEDBACK_SUBMITTED = "feedback_submitted"
    REMINDER_CREATED = "reminder_created"
    REMINDER_DELIVERED = "reminder_delivered"
    ERROR_OCCURRED = "error_occurred"
    API_REQUEST = "api_request"


class SystemMetric(BaseModel):
    """System metric data point"""
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    metric_type: MetricType = Field(..., description="Type of metric")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Metric timestamp")
    labels: Dict[str, str] = Field(default={}, description="Metric labels/tags")


class AnalyticsEventCreateRequest(BaseModel):
    """Create analytics event request"""
    event_type: EventType = Field(..., description="Type of event")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    event_data: Dict[str, Any] = Field(default={}, description="Event-specific data")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "user_login",
                "user_id": "60f7b1b3b3f3b3b3b3b3b3b3",
                "session_id": "sess_123456789",
                "event_data": {
                    "login_method": "phone_number",
                    "success": True,
                    "ip_address": "192.168.1.1"
                },
                "metadata": {
                    "user_agent": "Mozilla/5.0...",
                    "app_version": "1.0.0"
                }
            }
        }


class AnalyticsEventResponse(BaseResponse):
    """Analytics event response"""
    event_type: EventType = Field(..., description="Type of event")
    user_id: Optional[str] = Field(default=None, description="Associated user ID")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    event_data: Dict[str, Any] = Field(..., description="Event-specific data")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")
    processed_at: datetime = Field(..., description="Event processing timestamp")


class MetricCreateRequest(BaseModel):
    """Create metric request"""
    name: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    metric_type: MetricType = Field(..., description="Type of metric")
    labels: Optional[Dict[str, str]] = Field(default={}, description="Metric labels/tags")


class AnalyticsQueryRequest(BaseModel):
    """Analytics query request"""
    timeframe: AnalyticsTimeframe = Field(..., description="Time range for analytics")
    start_date: Optional[datetime] = Field(default=None, description="Start date (overrides timeframe)")
    end_date: Optional[datetime] = Field(default=None, description="End date (overrides timeframe)")
    event_types: Optional[List[EventType]] = Field(default=None, description="Filter by event types")
    user_ids: Optional[List[str]] = Field(default=None, description="Filter by user IDs")
    group_by: Optional[List[str]] = Field(default=None, description="Group results by fields")
    metrics: Optional[List[str]] = Field(default=None, description="Specific metrics to include")


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    total_users: int = Field(..., description="Total registered users")
    active_users_today: int = Field(..., description="Active users today")
    active_users_week: int = Field(..., description="Active users this week")
    active_users_month: int = Field(..., description="Active users this month")
    total_conversations: int = Field(..., description="Total conversations")
    conversations_today: int = Field(..., description="Conversations today")
    total_messages: int = Field(..., description="Total messages")
    messages_today: int = Field(..., description="Messages today")
    total_feedback: int = Field(..., description="Total feedback submissions")
    feedback_today: int = Field(..., description="Feedback today")
    average_rating: float = Field(..., description="Average user rating")
    total_reminders: int = Field(..., description="Total reminders")
    active_reminders: int = Field(..., description="Active reminders")
    reminders_delivered_today: int = Field(..., description="Reminders delivered today")
    system_uptime: float = Field(..., description="System uptime percentage")
    api_response_time: float = Field(..., description="Average API response time (ms)")


class UserEngagementResponse(BaseModel):
    """User engagement analytics response"""
    timeframe: str = Field(..., description="Analytics timeframe")
    total_sessions: int = Field(..., description="Total user sessions")
    unique_users: int = Field(..., description="Unique active users")
    average_session_duration: float = Field(..., description="Average session duration (minutes)")
    messages_per_session: float = Field(..., description="Average messages per session")
    conversation_completion_rate: float = Field(..., description="Conversation completion rate")
    user_retention_rate: float = Field(..., description="User retention rate")
    daily_active_users: List[Dict[str, Any]] = Field(..., description="Daily active users trend")
    popular_features: List[Dict[str, Any]] = Field(..., description="Most used features")


class SystemPerformanceResponse(BaseModel):
    """System performance metrics response"""
    api_requests_total: int = Field(..., description="Total API requests")
    api_requests_successful: int = Field(..., description="Successful API requests")
    api_error_rate: float = Field(..., description="API error rate percentage")
    average_response_time: float = Field(..., description="Average response time (ms)")
    database_queries_total: int = Field(..., description="Total database queries")
    database_query_time: float = Field(..., description="Average database query time (ms)")
    memory_usage: float = Field(..., description="Memory usage percentage")
    cpu_usage: float = Field(..., description="CPU usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    active_connections: int = Field(..., description="Active database connections")
    response_time_distribution: Dict[str, int] = Field(..., description="Response time distribution")


class AuditLogCreateRequest(BaseModel):
    """Create audit log entry request"""
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(default=None, description="ID of affected resource")
    user_id: Optional[str] = Field(default=None, description="User who performed action")
    ip_address: Optional[str] = Field(default=None, description="IP address of request")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    changes: Optional[Dict[str, Any]] = Field(default={}, description="Changes made")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class AuditLogResponse(BaseResponse):
    """Audit log entry response"""
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(default=None, description="ID of affected resource")
    user_id: Optional[str] = Field(default=None, description="User who performed action")
    ip_address: Optional[str] = Field(default=None, description="IP address of request")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    changes: Dict[str, Any] = Field(default={}, description="Changes made")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")
    timestamp: datetime = Field(..., description="Action timestamp")
