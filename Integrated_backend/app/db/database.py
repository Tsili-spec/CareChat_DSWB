import motor.motor_asyncio
from beanie import init_beanie
from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.models import Patient, Feedback, Reminder, ReminderDelivery

logger = get_logger(__name__)

class Database:
    client: motor.motor_asyncio.AsyncIOMotorClient = None
    database: motor.motor_asyncio.AsyncIOMotorDatabase = None

db = Database()

async def connect_to_mongo():
    """Initialize database connection"""
    try:
        logger.info(f"Connecting to MongoDB at: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
        
        # Initialize the database client and connection with proper timeouts
        db.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.DATABASE_URL,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        db.database = db.client.carechat  # Explicitly use carechat database
        
        # Test the connection first
        await db.client.admin.command('ping')
        logger.info("✅ Successfully connected to MongoDB!")
        
        # Initialize Beanie ODM with the models
        await init_beanie(
            database=db.database,
            document_models=[Patient, Feedback, Reminder, ReminderDelivery]
        )
        logger.info("✅ Beanie ODM initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️  Server will start without database connection")
        logger.warning("⚠️  Database-dependent features will not work")
        # Don't raise the exception - let the server start anyway

async def close_mongo_connection():
    """Close database connection"""
    if db.client is not None:
        db.client.close()
        logger.info("MongoDB connection closed")

async def get_db():
    """Dependency to get database connection"""
    return db.database
