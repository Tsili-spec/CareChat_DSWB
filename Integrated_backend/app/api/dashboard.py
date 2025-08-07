from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
from io import StringIO
import csv
import ast
from datetime import datetime
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

@router.get("/dashboard/download-feedback-csv",
            summary="Download feedback data as CSV",
            description="Download all feedback data in CSV format")
async def download_feedback_csv(
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD format)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD format)"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (positive/negative/neutral)"),
    urgency: Optional[str] = Query(None, description="Filter by urgency (urgent/not urgent)")
):
    """
    Download feedback data as CSV file with optional filters.
    
    **Query Parameters:**
    - start_date: Filter feedback from this date onwards (YYYY-MM-DD)
    - end_date: Filter feedback up to this date (YYYY-MM-DD)
    - sentiment: Filter by sentiment (positive/negative/neutral)
    - urgency: Filter by urgency level (urgent/not urgent)
    
    **Response:** CSV file containing feedback data with columns:
    - Date: Created date of feedback
    - Language: Language of the feedback
    - Rating: Rating given (1-5)
    - Sentiment: Sentiment analysis result (positive/negative/neutral)
    - Topic: Topics identified in feedback
    - Urgency: Urgency level (urgent/not urgent)
    """
    try:
        # Build query filters
        query_filters = {}
        
        # Date range filters
        if start_date or end_date:
            date_filter = {}
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    date_filter["$gte"] = start_dt
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid start_date format. Use YYYY-MM-DD"
                    )
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    # Add one day to include the entire end date
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    date_filter["$lte"] = end_dt
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid end_date format. Use YYYY-MM-DD"
                    )
            query_filters["created_at"] = date_filter
        
        # Sentiment filter
        if sentiment:
            query_filters["sentiment"] = sentiment
        
        # Urgency filter
        if urgency:
            query_filters["urgency"] = urgency
        
        # Fetch feedback data with filters
        if query_filters:
            feedback_list = await Feedback.find(query_filters).to_list()
        else:
            feedback_list = await Feedback.find().to_list()
        
        # Create CSV content in memory
        output = StringIO()
        writer = csv.writer(output, delimiter='\t', quoting=csv.QUOTE_ALL)  # Quote all fields to prevent column splitting
        
        # Write header
        writer.writerow(['Date', 'Language', 'Rating', 'Sentiment', 'Topic', 'Urgency'])
        
        # Write data rows
        for feedback in feedback_list:
            # Format date or use "Unknown" if no date
            date_str = feedback.created_at.strftime('%Y-%m-%d') if feedback.created_at else "Unknown"
            
            # Handle rating - use rating value or empty string
            rating_str = str(feedback.rating) if feedback.rating else ""
            
            # Handle sentiment
            sentiment_str = feedback.sentiment if feedback.sentiment else ""
            
            # Handle topic - format as {topic1,topic2} or empty string, ensuring it stays in one cell
            topic_str = ""
            if feedback.topic:
                try:
                    if isinstance(feedback.topic, list):
                        # If topic is a list, format as {topic1,topic2}
                        clean_topics = [str(topic).strip() for topic in feedback.topic if topic]
                        if clean_topics:
                            topic_str = "{" + ",".join(clean_topics) + "}"
                    elif isinstance(feedback.topic, str):
                        # If topic is a string, handle different formats
                        topic_clean = feedback.topic.strip()
                        if topic_clean:
                            # Remove any existing brackets and parse
                            topic_clean = topic_clean.strip('{}[]')
                            
                            # Try to parse if it looks like a list representation
                            if topic_clean.startswith("'") or topic_clean.startswith('"'):
                                # Handle string representations like "['topic1', 'topic2']"
                                try:
                                    parsed_topics = ast.literal_eval('[' + topic_clean + ']')
                                    if isinstance(parsed_topics, list):
                                        clean_topics = [str(t).strip().strip("'\"") for t in parsed_topics if t]
                                        topic_str = "{" + ",".join(clean_topics) + "}"
                                    else:
                                        topic_str = "{" + topic_clean + "}"
                                except:
                                    # If parsing fails, treat as comma-separated string
                                    topics = [t.strip().strip("'\"") for t in topic_clean.split(',') if t.strip()]
                                    topic_str = "{" + ",".join(topics) + "}"
                            else:
                                # Simple comma-separated or single topic
                                topics = [t.strip() for t in topic_clean.split(',') if t.strip()]
                                topic_str = "{" + ",".join(topics) + "}"
                except Exception as e:
                    # If anything fails, just use the original topic as string
                    logger.warning(f"Error processing topic for feedback: {e}")
                    topic_str = "{" + str(feedback.topic).strip('{}[]') + "}"
            
            # Handle urgency
            urgency_str = feedback.urgency if feedback.urgency else "not urgent"
            
            # Handle language
            language_str = feedback.language if feedback.language else "en"
            
            writer.writerow([
                date_str,
                language_str,
                rating_str,
                sentiment_str,
                topic_str,
                urgency_str
            ])
        
        # Prepare the response
        output.seek(0)
        csv_content = output.getvalue()
        output.close()
        
        # Create the streaming response
        def generate():
            yield csv_content
        
        # Generate filename with current timestamp and filters
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filter_suffix = ""
        if start_date or end_date or sentiment or urgency:
            filter_parts = []
            if start_date: filter_parts.append(f"from_{start_date}")
            if end_date: filter_parts.append(f"to_{end_date}")
            if sentiment: filter_parts.append(f"sentiment_{sentiment}")
            if urgency: filter_parts.append(f"urgency_{urgency.replace(' ', '_')}")
            filter_suffix = "_" + "_".join(filter_parts)
        
        filename = f"feedback_data_{timestamp}{filter_suffix}.csv"
        
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'text/csv; charset=utf-8'
        }
        
        return StreamingResponse(
            generate(),
            media_type='text/csv',
            headers=headers
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        logger.error(f"Error generating CSV download: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating CSV file"
        )
