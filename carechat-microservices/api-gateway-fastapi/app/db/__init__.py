"""
Database package initialization
MongoDB connection and session management for CareChat microservices
"""

from .database import (
    MongoDB,
    db,
    connect_to_mongo,
    close_mongo_connection,
    ensure_collections,
    create_indexes,
    get_users_collection,
    get_conversations_collection,
    get_messages_collection,
    get_feedback_sessions_collection,
    get_smart_reminders_collection,
    get_reminder_deliveries_collection,
    get_notification_templates_collection,
    get_system_analytics_collection,
    get_system_audit_log_collection
)

__all__ = [
    # Core database classes and functions
    "MongoDB",
    "db", 
    "connect_to_mongo",
    "close_mongo_connection",
    "ensure_collections", 
    "create_indexes",
    
    # Collection accessor functions
    "get_users_collection",
    "get_conversations_collection", 
    "get_messages_collection",
    "get_feedback_sessions_collection",
    "get_smart_reminders_collection",
    "get_reminder_deliveries_collection",
    "get_notification_templates_collection",
    "get_system_analytics_collection",
    "get_system_audit_log_collection"
]
