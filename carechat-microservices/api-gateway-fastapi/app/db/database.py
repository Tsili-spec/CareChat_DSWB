from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


db = MongoDB()


async def connect_to_mongo():
    """Create database connection"""
    try:
        logger.info("Connecting to MongoDB...")
        logger.info(f"MongoDB URL: {settings.MONGODB_URL}")
        logger.info(f"Database: {settings.MONGODB_DATABASE}")
        
        # Create the motor client
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )
        
        # Get the database
        db.database = db.client[settings.MONGODB_DATABASE]
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Initialize collections and indexes
        await ensure_collections()
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


async def ensure_collections():
    """Ensure required collections exist with proper validation"""
    try:
        collections = [
            "users",
            "conversations",
            "chat_messages",
            "feedback_sessions",
            "smart_reminders",
            "reminder_deliveries",
            "notification_templates",
            "system_analytics",
            "system_audit_log"
        ]
        
        existing_collections = await db.database.list_collection_names()
        
        for collection_name in collections:
            if collection_name not in existing_collections:
                logger.info(f"Creating collection: {collection_name}")
                await db.database.create_collection(collection_name)
            else:
                logger.info(f"Collection {collection_name} already exists")
                
    except Exception as e:
        logger.error(f"Error ensuring collections: {e}")
        # Don't raise - we want to continue even if some collections exist


async def create_indexes():
    """Create indexes for optimal performance - safely"""
    try:
        logger.info("Creating database indexes...")
        
        # Users collection indexes
        users_collection = db.database.users
        await users_collection.create_index("user_id", unique=True, background=True)
        await users_collection.create_index("phone_number", unique=True, sparse=True, background=True)
        await users_collection.create_index("email", unique=True, sparse=True, background=True)
        await users_collection.create_index("account_status.is_active", background=True)
        await users_collection.create_index("account_status.is_verified", background=True)
        await users_collection.create_index("preferred_language", background=True)
        await users_collection.create_index("created_at", background=True)
        
        # Conversations collection indexes
        conversations_collection = db.database.conversations
        await conversations_collection.create_index("conversation_id", unique=True, background=True)
        await conversations_collection.create_index("user_id", background=True)
        await conversations_collection.create_index([("user_id", 1), ("metadata.status", 1), ("updated_at", -1)], background=True)
        await conversations_collection.create_index("metadata.status", background=True)
        await conversations_collection.create_index("metadata.conversation_type", background=True)
        await conversations_collection.create_index("metadata.department", sparse=True, background=True)
        await conversations_collection.create_index("metadata.priority", background=True)
        await conversations_collection.create_index("created_at", background=True)
        
        # Chat messages collection indexes
        messages_collection = db.database.chat_messages
        await messages_collection.create_index("message_id", unique=True, background=True)
        await messages_collection.create_index("conversation_id", background=True)
        await messages_collection.create_index([("conversation_id", 1), ("timestamp", 1)], background=True)
        await messages_collection.create_index("role", background=True)
        await messages_collection.create_index("timestamp", background=True)
        
        # Feedback sessions collection indexes
        feedback_collection = db.database.feedback_sessions
        await feedback_collection.create_index("session_id", unique=True, background=True)
        await feedback_collection.create_index("user_id", background=True)
        await feedback_collection.create_index([("user_id", 1), ("created_at", -1)], background=True)
        await feedback_collection.create_index("session_info.status", background=True)
        await feedback_collection.create_index("session_info.session_type", background=True)
        await feedback_collection.create_index("session_info.department", sparse=True, background=True)
        
        # Smart reminders collection indexes
        reminders_collection = db.database.smart_reminders
        await reminders_collection.create_index("reminder_id", unique=True, background=True)
        await reminders_collection.create_index("user_id", background=True)
        await reminders_collection.create_index([("user_id", 1), ("reminder_config.status", 1)], background=True)
        await reminders_collection.create_index("reminder_config.status", background=True)
        await reminders_collection.create_index("reminder_config.type", background=True)
        await reminders_collection.create_index("reminder_config.priority", background=True)
        await reminders_collection.create_index("schedule.patterns.start_date", background=True)
        await reminders_collection.create_index("delivery_tracking.next_scheduled_delivery", sparse=True, background=True)
        
        # Reminder deliveries collection indexes
        deliveries_collection = db.database.reminder_deliveries
        await deliveries_collection.create_index("delivery_id", unique=True, background=True)
        await deliveries_collection.create_index("reminder_id", background=True)
        await deliveries_collection.create_index("user_id", background=True)
        await deliveries_collection.create_index([("reminder_id", 1), ("scheduled_time", -1)], background=True)
        await deliveries_collection.create_index("scheduled_time", background=True)
        await deliveries_collection.create_index("delivery_info.status", background=True)
        await deliveries_collection.create_index("delivery_info.method", background=True)
        
        # System analytics collection indexes
        analytics_collection = db.database.system_analytics
        await analytics_collection.create_index("analytics_id", unique=True, background=True)
        await analytics_collection.create_index("metric_info.category", background=True)
        await analytics_collection.create_index("metric_info.type", background=True)
        await analytics_collection.create_index("time_dimension.timestamp", background=True)
        await analytics_collection.create_index([("time_dimension.date", 1), ("metric_info.category", 1)], background=True)
        
        # System audit log collection indexes
        audit_collection = db.database.system_audit_log
        await audit_collection.create_index("log_id", unique=True, background=True)
        await audit_collection.create_index("action_info.entity_type", background=True)
        await audit_collection.create_index("action_info.entity_id", sparse=True, background=True)
        await audit_collection.create_index("user_context.user_id", sparse=True, background=True)
        await audit_collection.create_index("timestamp", background=True)
        await audit_collection.create_index([("action_info.entity_type", 1), ("timestamp", -1)], background=True)
        
        logger.info("Successfully created all database indexes")
        
    except Exception as e:
        logger.warning(f"Some indexes may already exist or failed to create: {e}")
        # Don't raise - we want to continue even if some indexes exist


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if db.database is None:
        raise Exception("Database not initialized")
    return db.database


# Collection getters for easy access
async def get_users_collection():
    database = await get_database()
    return database.users


async def get_conversations_collection():
    database = await get_database()
    return database.conversations


async def get_messages_collection():
    database = await get_database()
    return database.chat_messages


async def get_feedback_sessions_collection():
    database = await get_database()
    return database.feedback_sessions


async def get_smart_reminders_collection():
    database = await get_database()
    return database.smart_reminders


async def get_reminder_deliveries_collection():
    database = await get_database()
    return database.reminder_deliveries


async def get_notification_templates_collection():
    database = await get_database()
    return database.notification_templates


async def get_system_analytics_collection():
    database = await get_database()
    return database.system_analytics


async def get_system_audit_log_collection():
    database = await get_database()
    return database.system_audit_log
