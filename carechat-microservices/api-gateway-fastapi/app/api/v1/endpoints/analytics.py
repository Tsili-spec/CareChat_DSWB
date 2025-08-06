from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.db.database import (
    get_system_analytics_collection,
    get_users_collection,
    get_conversations_collection,
    get_feedback_sessions_collection,
    get_smart_reminders_collection
)
from app.models import User
from app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/user-stats")
async def get_user_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get user analytics and statistics"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get collections
    conversations_collection = await get_conversations_collection()
    feedback_collection = await get_feedback_sessions_collection()
    reminders_collection = await get_smart_reminders_collection()
    
    # Get conversation stats
    conversation_stats = await conversations_collection.aggregate([
        {
            "$match": {
                "user_id": current_user.user_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_conversations": {"$sum": 1},
                "total_messages": {"$sum": {"$size": "$messages"}},
                "avg_messages_per_conversation": {"$avg": {"$size": "$messages"}},
                "conversation_types": {"$push": "$conversation_type"}
            }
        }
    ]).to_list(length=1)
    
    # Get feedback stats
    feedback_stats = await feedback_collection.aggregate([
        {
            "$match": {
                "user_id": current_user.user_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_feedback_sessions": {"$sum": 1},
                "total_feedback_entries": {"$sum": {"$size": "$feedback_entries"}},
                "avg_rating": {"$avg": {"$avg": "$feedback_entries.rating"}}
            }
        }
    ]).to_list(length=1)
    
    # Get reminder stats
    reminder_stats = await reminders_collection.aggregate([
        {
            "$match": {
                "user_id": current_user.user_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_reminders": {"$sum": 1},
                "active_reminders": {
                    "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                },
                "completed_reminders": {
                    "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                }
            }
        }
    ]).to_list(length=1)
    
    # Compile results
    result = {
        "user_id": current_user.user_id,
        "analysis_period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        },
        "conversations": conversation_stats[0] if conversation_stats else {
            "total_conversations": 0,
            "total_messages": 0,
            "avg_messages_per_conversation": 0,
            "conversation_types": []
        },
        "feedback": feedback_stats[0] if feedback_stats else {
            "total_feedback_sessions": 0,
            "total_feedback_entries": 0,
            "avg_rating": 0
        },
        "reminders": reminder_stats[0] if reminder_stats else {
            "total_reminders": 0,
            "active_reminders": 0,
            "completed_reminders": 0
        }
    }
    
    return result


@router.get("/usage-trends")
async def get_usage_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get usage trends over time"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    conversations_collection = await get_conversations_collection()
    
    # Get daily conversation trends
    daily_trends = await conversations_collection.aggregate([
        {
            "$match": {
                "user_id": current_user.user_id,
                "created_at": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                    "day": {"$dayOfMonth": "$created_at"}
                },
                "conversations": {"$sum": 1},
                "messages": {"$sum": {"$size": "$messages"}}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]).to_list(length=None)
    
    # Format trends data
    trends = []
    for trend in daily_trends:
        date_obj = datetime(
            trend["_id"]["year"],
            trend["_id"]["month"],
            trend["_id"]["day"]
        )
        trends.append({
            "date": date_obj.strftime("%Y-%m-%d"),
            "conversations": trend["conversations"],
            "messages": trend["messages"]
        })
    
    return {
        "user_id": current_user.user_id,
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        },
        "daily_trends": trends
    }


@router.get("/system-health")
async def get_system_health(
    current_user: User = Depends(get_current_user)
):
    """Get system health metrics (basic version for users)"""
    # Get basic system stats
    users_collection = await get_users_collection()
    conversations_collection = await get_conversations_collection()
    
    # Count active users (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    active_users = await users_collection.count_documents({
        "account_status.last_login": {"$gte": yesterday}
    })
    
    # Count total conversations today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_conversations = await conversations_collection.count_documents({
        "created_at": {"$gte": today_start}
    })
    
    return {
        "timestamp": datetime.utcnow(),
        "system_status": "operational",
        "metrics": {
            "active_users_24h": active_users,
            "conversations_today": today_conversations
        }
    }


@router.get("/engagement-metrics")
async def get_engagement_metrics(
    current_user: User = Depends(get_current_user)
):
    """Get user engagement metrics"""
    # Calculate user engagement based on activity
    conversations_collection = await get_conversations_collection()
    feedback_collection = await get_feedback_sessions_collection()
    
    # Get last 30 days activity
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Count conversations in last 30 days
    recent_conversations = await conversations_collection.count_documents({
        "user_id": current_user.user_id,
        "created_at": {"$gte": thirty_days_ago}
    })
    
    # Count feedback sessions in last 30 days
    recent_feedback = await feedback_collection.count_documents({
        "user_id": current_user.user_id,
        "created_at": {"$gte": thirty_days_ago}
    })
    
    # Calculate engagement score (simple algorithm)
    engagement_score = min(100, (recent_conversations * 10) + (recent_feedback * 15))
    
    # Determine engagement level
    if engagement_score >= 80:
        engagement_level = "high"
    elif engagement_score >= 40:
        engagement_level = "medium"
    else:
        engagement_level = "low"
    
    return {
        "user_id": current_user.user_id,
        "engagement_score": engagement_score,
        "engagement_level": engagement_level,
        "metrics": {
            "conversations_30d": recent_conversations,
            "feedback_sessions_30d": recent_feedback
        },
        "calculated_at": datetime.utcnow()
    }


@router.get("/conversation-analytics")
async def get_conversation_analytics(
    conversation_id: Optional[str] = Query(None, description="Specific conversation ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get conversation analytics"""
    conversations_collection = await get_conversations_collection()
    
    # Build query
    query = {"user_id": current_user.user_id}
    if conversation_id:
        query["conversation_id"] = conversation_id
    else:
        # Filter by date range if not specific conversation
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        query["created_at"] = {"$gte": start_date, "$lte": end_date}
    
    # Get conversation analytics
    analytics = await conversations_collection.aggregate([
        {"$match": query},
        {
            "$project": {
                "conversation_id": 1,
                "conversation_type": 1,
                "status": 1,
                "created_at": 1,
                "message_count": {"$size": "$messages"},
                "user_messages": {
                    "$size": {
                        "$filter": {
                            "input": "$messages",
                            "cond": {"$eq": ["$$this.sender_type", "user"]}
                        }
                    }
                },
                "assistant_messages": {
                    "$size": {
                        "$filter": {
                            "input": "$messages",
                            "cond": {"$eq": ["$$this.sender_type", "assistant"]}
                        }
                    }
                },
                "avg_response_time": {"$literal": 0}  # Placeholder - would need message timestamps
            }
        }
    ]).to_list(length=None)
    
    if conversation_id and not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Calculate summary stats if multiple conversations
    if not conversation_id and analytics:
        total_conversations = len(analytics)
        total_messages = sum(conv["message_count"] for conv in analytics)
        avg_messages_per_conversation = total_messages / total_conversations if total_conversations > 0 else 0
        
        summary = {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(avg_messages_per_conversation, 2),
            "conversation_types": list(set(conv["conversation_type"] for conv in analytics))
        }
        
        return {
            "user_id": current_user.user_id,
            "summary": summary,
            "conversations": analytics
        }
    
    return {
        "user_id": current_user.user_id,
        "conversations": analytics
    }
