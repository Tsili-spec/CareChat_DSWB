from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.db.database import get_feedback_sessions_collection
from app.models import User, FeedbackSession
from app.schemas.feedback import (
    FeedbackSessionCreateRequest,
    FeedbackSessionResponse,
    FeedbackSessionUpdateRequest,
    FeedbackEntryCreateRequest
)
from app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=FeedbackSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback_session(
    session_data: FeedbackSessionCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new feedback session"""
    feedback_collection = await get_feedback_sessions_collection()
    
    # Create feedback session
    feedback_session = FeedbackSession(
        user_id=current_user.user_id,
        session_type=session_data.session_type,
        conversation_id=session_data.conversation_id,
        metadata=session_data.metadata or {},
        feedback_entries=[]
    )
    
    # Insert feedback session
    session_dict = feedback_session.dict(by_alias=True, exclude_none=True)
    result = await feedback_collection.insert_one(session_dict)
    
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create feedback session"
        )
    
    logger.info(f"New feedback session created: {feedback_session.session_id} for user: {current_user.user_id}")
    
    return FeedbackSessionResponse(
        session_id=feedback_session.session_id,
        user_id=feedback_session.user_id,
        session_type=feedback_session.session_type,
        conversation_id=feedback_session.conversation_id,
        status=feedback_session.status,
        metadata=feedback_session.metadata,
        feedback_count=len(feedback_session.feedback_entries),
        created_at=feedback_session.created_at,
        updated_at=feedback_session.updated_at
    )


@router.get("/", response_model=List[FeedbackSessionResponse])
async def get_feedback_sessions(
    skip: int = Query(0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of sessions to retrieve"),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    conversation_id: Optional[str] = Query(None, description="Filter by conversation ID"),
    current_user: User = Depends(get_current_user)
):
    """Get user's feedback sessions with pagination and filtering"""
    feedback_collection = await get_feedback_sessions_collection()
    
    # Build query
    query = {"user_id": current_user.user_id}
    if session_type:
        query["session_type"] = session_type
    if status:
        query["status"] = status
    if conversation_id:
        query["conversation_id"] = conversation_id
    
    # Get feedback sessions
    cursor = feedback_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    sessions = []
    
    async for session_doc in cursor:
        session = FeedbackSession(**session_doc)
        sessions.append(FeedbackSessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            session_type=session.session_type,
            conversation_id=session.conversation_id,
            status=session.status,
            metadata=session.metadata,
            feedback_count=len(session.feedback_entries),
            created_at=session.created_at,
            updated_at=session.updated_at
        ))
    
    return sessions


@router.get("/{session_id}", response_model=FeedbackSession)
async def get_feedback_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get feedback session by ID"""
    feedback_collection = await get_feedback_sessions_collection()
    
    session_doc = await feedback_collection.find_one({
        "session_id": session_id,
        "user_id": current_user.user_id
    })
    
    if not session_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback session not found"
        )
    
    return FeedbackSession(**session_doc)


@router.put("/{session_id}", response_model=FeedbackSessionResponse)
async def update_feedback_session(
    session_id: str,
    session_update: FeedbackSessionUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update feedback session"""
    feedback_collection = await get_feedback_sessions_collection()
    
    # Check if session exists and belongs to user
    session_doc = await feedback_collection.find_one({
        "session_id": session_id,
        "user_id": current_user.user_id
    })
    
    if not session_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback session not found"
        )
    
    # Build update data
    update_data = {}
    if session_update.status is not None:
        update_data["status"] = session_update.status
    if session_update.metadata is not None:
        update_data["metadata"] = session_update.metadata
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        # Update session
        result = await feedback_collection.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback session not found"
            )
    
    # Get updated session
    updated_session_doc = await feedback_collection.find_one({"session_id": session_id})
    updated_session = FeedbackSession(**updated_session_doc)
    
    logger.info(f"Feedback session updated: {session_id}")
    
    return FeedbackSessionResponse(
        session_id=updated_session.session_id,
        user_id=updated_session.user_id,
        session_type=updated_session.session_type,
        conversation_id=updated_session.conversation_id,
        status=updated_session.status,
        metadata=updated_session.metadata,
        feedback_count=len(updated_session.feedback_entries),
        created_at=updated_session.created_at,
        updated_at=updated_session.updated_at
    )


@router.delete("/{session_id}")
async def delete_feedback_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete feedback session"""
    feedback_collection = await get_feedback_sessions_collection()
    
    # Check if session exists and belongs to user
    result = await feedback_collection.delete_one({
        "session_id": session_id,
        "user_id": current_user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback session not found"
        )
    
    logger.info(f"Feedback session deleted: {session_id}")
    
    return {"message": "Feedback session deleted successfully"}


@router.post("/{session_id}/feedback")
async def add_feedback_entry(
    session_id: str,
    feedback_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Add feedback entry to session"""
    feedback_collection = await get_feedback_sessions_collection()
    
    # Check if session exists and belongs to user
    session_doc = await feedback_collection.find_one({
        "session_id": session_id,
        "user_id": current_user.user_id
    })
    
    if not session_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback session not found"
        )
    
    # Create feedback entry
    feedback_entry = {
        "entry_id": f"fb_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
        "feedback_type": feedback_data.get("feedback_type", "general"),
        "rating": feedback_data.get("rating"),
        "comment": feedback_data.get("comment"),
        "tags": feedback_data.get("tags", []),
        "timestamp": datetime.utcnow(),
        "metadata": feedback_data.get("metadata", {})
    }
    
    # Add feedback entry to session
    result = await feedback_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {"feedback_entries": feedback_entry},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback session not found"
        )
    
    logger.info(f"Feedback entry added to session: {session_id}")
    
    return {"message": "Feedback entry added successfully", "entry_id": feedback_entry["entry_id"]}


@router.get("/{session_id}/feedback")
async def get_feedback_entries(
    session_id: str,
    skip: int = Query(0, ge=0, description="Number of entries to skip"),
    limit: int = Query(50, ge=1, le=500, description="Number of entries to retrieve"),
    current_user: User = Depends(get_current_user)
):
    """Get feedback entries from session"""
    feedback_collection = await get_feedback_sessions_collection()
    
    # Use aggregation to get paginated feedback entries
    pipeline = [
        {
            "$match": {
                "session_id": session_id,
                "user_id": current_user.user_id
            }
        },
        {
            "$project": {
                "feedback_entries": {
                    "$slice": ["$feedback_entries", skip, limit]
                }
            }
        }
    ]
    
    cursor = feedback_collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback session not found"
        )
    
    return {
        "session_id": session_id,
        "feedback_entries": result[0].get("feedback_entries", [])
    }


@router.get("/{session_id}/analytics")
async def get_feedback_analytics(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get feedback analytics for session"""
    feedback_collection = await get_feedback_sessions_collection()
    
    # Use aggregation to get analytics
    pipeline = [
        {
            "$match": {
                "session_id": session_id,
                "user_id": current_user.user_id
            }
        },
        {
            "$project": {
                "session_id": 1,
                "session_type": 1,
                "status": 1,
                "created_at": 1,
                "feedback_count": {"$size": "$feedback_entries"},
                "average_rating": {"$avg": "$feedback_entries.rating"},
                "rating_distribution": {
                    "$reduce": {
                        "input": "$feedback_entries",
                        "initialValue": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                        "in": {
                            "$mergeObjects": [
                                "$$value",
                                {
                                    "$cond": [
                                        {"$eq": ["$$this.rating", 1]},
                                        {"1": {"$add": [{"$getField": {"field": "1", "input": "$$value"}}, 1]}},
                                        {
                                            "$cond": [
                                                {"$eq": ["$$this.rating", 2]},
                                                {"2": {"$add": [{"$getField": {"field": "2", "input": "$$value"}}, 1]}},
                                                {
                                                    "$cond": [
                                                        {"$eq": ["$$this.rating", 3]},
                                                        {"3": {"$add": [{"$getField": {"field": "3", "input": "$$value"}}, 1]}},
                                                        {
                                                            "$cond": [
                                                                {"$eq": ["$$this.rating", 4]},
                                                                {"4": {"$add": [{"$getField": {"field": "4", "input": "$$value"}}, 1]}},
                                                                {"5": {"$add": [{"$getField": {"field": "5", "input": "$$value"}}, 1]}}
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
    ]
    
    cursor = feedback_collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback session not found"
        )
    
    return result[0]
