"""
MongoDB Collections Management
Provides collection accessor functions for different data types
"""
from typing import AsyncIterator
from motor.motor_asyncio import AsyncIOMotorCollection
from .database import db


async def get_users_collection() -> AsyncIOMotorCollection:
    """Get users collection"""
    return db.database.users


async def get_conversations_collection() -> AsyncIOMotorCollection:
    """Get conversations collection"""
    return db.database.conversations


async def get_messages_collection() -> AsyncIOMotorCollection:
    """Get messages collection"""
    return db.database.messages


async def get_feedback_sessions_collection() -> AsyncIOMotorCollection:
    """Get feedback sessions collection"""
    return db.database.feedback_sessions


async def get_smart_reminders_collection() -> AsyncIOMotorCollection:
    """Get smart reminders collection"""
    return db.database.smart_reminders


async def get_reminder_deliveries_collection() -> AsyncIOMotorCollection:
    """Get reminder deliveries collection"""
    return db.database.reminder_deliveries


async def get_notification_templates_collection() -> AsyncIOMotorCollection:
    """Get notification templates collection"""
    return db.database.notification_templates


async def get_system_analytics_collection() -> AsyncIOMotorCollection:
    """Get system analytics collection"""
    return db.database.system_analytics


async def get_audit_log_collection() -> AsyncIOMotorCollection:
    """Get audit log collection"""
    return db.database.system_audit_log


# Health check functions
async def check_database_connection() -> bool:
    """Check if database connection is working"""
    try:
        # Try to list collections to verify connection
        await db.database.list_collection_names()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False


async def get_database_stats() -> dict:
    """Get database statistics"""
    try:
        stats = await db.database.command("dbStats")
        return {
            "database": stats.get("db"),
            "collections": stats.get("collections"),
            "objects": stats.get("objects"),
            "data_size": stats.get("dataSize"),
            "storage_size": stats.get("storageSize"),
            "index_size": stats.get("indexSize")
        }
    except Exception as e:
        print(f"Error getting database stats: {e}")
        return {}
