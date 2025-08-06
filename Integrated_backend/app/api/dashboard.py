from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from app.models.models import Patient, Feedback, Reminder, ReminderDelivery
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/dashboard/stats",
            summary="Get dashboard statistics",
            description="Get comprehensive dashboard statistics")
async def get_dashboard_stats():
    """
    Get comprehensive dashboard statistics.
    
    **Response:** Dictionary containing various statistics
    """
    try:
        # Patient statistics
        total_patients = await Patient.count()
        
        # Feedback statistics
        total_feedback = await Feedback.count()
        positive_feedback = await Feedback.find({"sentiment": "positive"}).count()
        negative_feedback = await Feedback.find({"sentiment": "negative"}).count()
        neutral_feedback = await Feedback.find({"sentiment": "neutral"}).count()
        urgent_feedback = await Feedback.find({"urgency": "urgent"}).count()
        
        # Reminder statistics
        total_reminders = await Reminder.count()
        active_reminders = await Reminder.find({"status": "active"}).count()
        
        # Delivery statistics
        total_deliveries = await ReminderDelivery.count()
        successful_deliveries = await ReminderDelivery.find({"delivery_status": "sent"}).count()
        failed_deliveries = await ReminderDelivery.find({"delivery_status": "failed"}).count()
        
        # Calculate percentages
        feedback_sentiment_breakdown = {
            "positive": {
                "count": positive_feedback,
                "percentage": round((positive_feedback / total_feedback * 100), 2) if total_feedback > 0 else 0
            },
            "negative": {
                "count": negative_feedback,
                "percentage": round((negative_feedback / total_feedback * 100), 2) if total_feedback > 0 else 0
            },
            "neutral": {
                "count": neutral_feedback,
                "percentage": round((neutral_feedback / total_feedback * 100), 2) if total_feedback > 0 else 0
            }
        }
        
        delivery_success_rate = round((successful_deliveries / total_deliveries * 100), 2) if total_deliveries > 0 else 0
        
        return {
            "patients": {
                "total": total_patients
            },
            "feedback": {
                "total": total_feedback,
                "urgent": urgent_feedback,
                "sentiment_breakdown": feedback_sentiment_breakdown
            },
            "reminders": {
                "total": total_reminders,
                "active": active_reminders
            },
            "deliveries": {
                "total": total_deliveries,
                "successful": successful_deliveries,
                "failed": failed_deliveries,
                "success_rate": delivery_success_rate
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating dashboard statistics"
        )

@router.get("/dashboard/recent-activity",
            summary="Get recent activity",
            description="Get recent activity across the system")
async def get_recent_activity():
    """
    Get recent activity across the system.
    
    **Response:** Dictionary containing recent activities
    """
    try:
        # Recent patients (last 10)
        recent_patients = await Patient.find().sort([("created_at", -1)]).limit(10).to_list()
        
        # Recent feedback (last 10)
        recent_feedback = await Feedback.find().sort([("created_at", -1)]).limit(10).to_list()
        
        # Recent reminders (last 10)
        recent_reminders = await Reminder.find().sort([("created_at", -1)]).limit(10).to_list()
        
        # Recent deliveries (last 10)
        recent_deliveries = await ReminderDelivery.find().sort([("sent_at", -1)]).limit(10).to_list()
        
        return {
            "recent_patients": [
                {
                    "patient_id": patient.patient_id,
                    "full_name": patient.full_name,
                    "phone_number": patient.phone_number,
                    "created_at": patient.created_at
                } for patient in recent_patients
            ],
            "recent_feedback": [
                {
                    "feedback_id": feedback.feedback_id,
                    "patient_id": feedback.patient_id,
                    "sentiment": feedback.sentiment,
                    "urgency": feedback.urgency,
                    "created_at": feedback.created_at
                } for feedback in recent_feedback
            ],
            "recent_reminders": [
                {
                    "reminder_id": reminder.reminder_id,
                    "patient_id": reminder.patient_id,
                    "title": reminder.title,
                    "status": reminder.status,
                    "created_at": reminder.created_at
                } for reminder in recent_reminders
            ],
            "recent_deliveries": [
                {
                    "delivery_id": delivery.delivery_id,
                    "reminder_id": delivery.reminder_id,
                    "delivery_status": delivery.delivery_status,
                    "sent_at": delivery.sent_at
                } for delivery in recent_deliveries
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving recent activity"
        )

@router.get("/dashboard/feedback-analytics",
            summary="Get feedback analytics",
            description="Get detailed feedback analytics")
async def get_feedback_analytics():
    """
    Get detailed feedback analytics.
    
    **Response:** Dictionary containing feedback analytics
    """
    try:
        # Topic analysis for negative feedback
        negative_feedback_list = await Feedback.find({"sentiment": "negative", "topic": {"$ne": None}}).to_list()
        
        topic_counts = {}
        for feedback in negative_feedback_list:
            if feedback.topic:
                topics = feedback.topic if isinstance(feedback.topic, list) else [feedback.topic]
                for topic in topics:
                    topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Sort topics by frequency
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Language distribution
        language_pipeline = [
            {"$group": {"_id": "$language", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        language_distribution = []
        async for doc in Feedback.aggregate(language_pipeline):
            language_distribution.append({
                "language": doc["_id"],
                "count": doc["count"]
            })
        
        # Rating distribution
        rating_pipeline = [
            {"$match": {"rating": {"$ne": None}}},
            {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        rating_distribution = []
        async for doc in Feedback.aggregate(rating_pipeline):
            rating_distribution.append({
                "rating": doc["_id"],
                "count": doc["count"]
            })
        
        return {
            "top_negative_topics": [
                {"topic": topic, "count": count} for topic, count in top_topics
            ],
            "language_distribution": language_distribution,
            "rating_distribution": rating_distribution
        }
        
    except Exception as e:
        logger.error(f"Error generating feedback analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating feedback analytics"
        )

@router.get("/dashboard/system-health",
            summary="Get system health status",
            description="Get system health and status information")
async def get_system_health():
    """
    Get system health and status information.
    
    **Response:** Dictionary containing system health data
    """
    try:
        from app.services.reminder_scheduler import reminder_scheduler
        from app.services.sms_service import sms_service
        
        # Database connectivity (if we get here, database is working)
        database_status = "healthy"
        
        # SMS service status
        sms_status = "configured" if sms_service.is_configured() else "not_configured"
        
        # Scheduler status
        scheduler_status = "running" if reminder_scheduler.is_running else "stopped"
        
        # Recent error count (you could implement this by checking logs)
        # For now, we'll return a placeholder
        recent_errors = 0
        
        return {
            "database": {
                "status": database_status,
                "message": "Database connection is healthy"
            },
            "sms_service": {
                "status": sms_status,
                "message": "SMS service is configured and ready" if sms_status == "configured" else "SMS service requires configuration"
            },
            "scheduler": {
                "status": scheduler_status,
                "message": f"Reminder scheduler is {scheduler_status}"
            },
            "overall_health": "healthy" if all([
                database_status == "healthy",
                sms_status == "configured",
                recent_errors == 0
            ]) else "warning",
            "recent_errors": recent_errors
        }
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return {
            "database": {
                "status": "error",
                "message": f"Database error: {str(e)}"
            },
            "overall_health": "error",
            "error_message": str(e)
        }
