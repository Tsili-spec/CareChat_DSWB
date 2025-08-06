"""
MongoDB Session and Dependency Management
Provides database dependencies and session management for FastAPI
"""
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from .database import db


async def get_database() -> AsyncIOMotorDatabase:
    """
    Database dependency for FastAPI endpoints
    Returns the MongoDB database instance
    """
    if not db.database:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return db.database


async def get_collection(collection_name: str) -> AsyncIOMotorCollection:
    """
    Get a specific collection by name
    
    Args:
        collection_name: Name of the collection to retrieve
        
    Returns:
        AsyncIOMotorCollection: The requested collection
    """
    database = await get_database()
    return database[collection_name]


class DatabaseTransaction:
    """
    Context manager for MongoDB transactions (if using replica set)
    Note: Transactions require MongoDB replica set or sharded cluster
    """
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        if db.client:
            self.session = await db.client.start_session()
            self.session.start_transaction()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.session.abort_transaction()
            else:
                await self.session.commit_transaction()
            await self.session.end_session()


async def with_transaction(operation):
    """
    Execute an operation within a MongoDB transaction
    
    Args:
        operation: Async function to execute within transaction
        
    Returns:
        Result of the operation
    """
    async with DatabaseTransaction() as session:
        return await operation(session)


# Collection-specific dependencies for FastAPI dependency injection
async def get_users_dependency() -> AsyncIOMotorCollection:
    """FastAPI dependency for users collection"""
    return await get_collection("users")


async def get_conversations_dependency() -> AsyncIOMotorCollection:
    """FastAPI dependency for conversations collection"""
    return await get_collection("conversations")


async def get_messages_dependency() -> AsyncIOMotorCollection:
    """FastAPI dependency for messages collection"""
    return await get_collection("messages")


async def get_feedback_sessions_dependency() -> AsyncIOMotorCollection:
    """FastAPI dependency for feedback sessions collection"""
    return await get_collection("feedback_sessions")


async def get_smart_reminders_dependency() -> AsyncIOMotorCollection:
    """FastAPI dependency for smart reminders collection"""
    return await get_collection("smart_reminders")


# Database health and monitoring
async def ping_database() -> bool:
    """
    Ping the database to check connectivity
    
    Returns:
        bool: True if database is responsive, False otherwise
    """
    try:
        database = await get_database()
        await database.command("ping")
        return True
    except Exception:
        return False


async def get_connection_info() -> dict:
    """
    Get MongoDB connection information
    
    Returns:
        dict: Connection information including server info
    """
    try:
        database = await get_database()
        server_info = await database.command("serverStatus")
        return {
            "host": server_info.get("host"),
            "version": server_info.get("version"),
            "uptime": server_info.get("uptime"),
            "connections": server_info.get("connections", {}),
            "network": server_info.get("network", {})
        }
    except Exception as e:
        return {"error": str(e)}
