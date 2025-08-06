from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.db.database import get_conversations_collection
from app.models import User, Conversation
from app.schemas.conversation import (
    ConversationCreateRequest, 
    ConversationResponse,
    ConversationUpdateRequest,
    MessageCreateRequest
)
from app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation"""
    conversations_collection = await get_conversations_collection()
    
    # Create conversation
    conversation = Conversation(
        user_id=current_user.user_id,
        conversation_type=conversation_data.conversation_type,
        metadata=conversation_data.metadata or {},
        messages=[]
    )
    
    # Insert conversation
    conversation_dict = conversation.dict(by_alias=True, exclude_none=True)
    result = await conversations_collection.insert_one(conversation_dict)
    
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )
    
    logger.info(f"New conversation created: {conversation.conversation_id} for user: {current_user.user_id}")
    
    return ConversationResponse(
        conversation_id=conversation.conversation_id,
        user_id=conversation.user_id,
        conversation_type=conversation.conversation_type,
        status=conversation.status,
        metadata=conversation.metadata,
        message_count=len(conversation.messages),
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = Query(0, ge=0, description="Number of conversations to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of conversations to retrieve"),
    conversation_type: Optional[str] = Query(None, description="Filter by conversation type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user)
):
    """Get user's conversations with pagination and filtering"""
    conversations_collection = await get_conversations_collection()
    
    # Build query
    query = {"user_id": current_user.user_id}
    if conversation_type:
        query["conversation_type"] = conversation_type
    if status:
        query["status"] = status
    
    # Get conversations
    cursor = conversations_collection.find(query).sort("updated_at", -1).skip(skip).limit(limit)
    conversations = []
    
    async for conv_doc in cursor:
        conversation = Conversation(**conv_doc)
        conversations.append(ConversationResponse(
            conversation_id=conversation.conversation_id,
            user_id=conversation.user_id,
            conversation_type=conversation.conversation_type,
            status=conversation.status,
            metadata=conversation.metadata,
            message_count=len(conversation.messages),
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        ))
    
    return conversations


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get conversation by ID"""
    conversations_collection = await get_conversations_collection()
    
    conversation_doc = await conversations_collection.find_one({
        "conversation_id": conversation_id,
        "user_id": current_user.user_id
    })
    
    if not conversation_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return Conversation(**conversation_doc)


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    conversation_update: ConversationUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update conversation"""
    conversations_collection = await get_conversations_collection()
    
    # Check if conversation exists and belongs to user
    conversation_doc = await conversations_collection.find_one({
        "conversation_id": conversation_id,
        "user_id": current_user.user_id
    })
    
    if not conversation_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Build update data
    update_data = {}
    if conversation_update.status is not None:
        update_data["status"] = conversation_update.status
    if conversation_update.metadata is not None:
        update_data["metadata"] = conversation_update.metadata
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        # Update conversation
        result = await conversations_collection.update_one(
            {"conversation_id": conversation_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
    
    # Get updated conversation
    updated_conv_doc = await conversations_collection.find_one({"conversation_id": conversation_id})
    updated_conversation = Conversation(**updated_conv_doc)
    
    logger.info(f"Conversation updated: {conversation_id}")
    
    return ConversationResponse(
        conversation_id=updated_conversation.conversation_id,
        user_id=updated_conversation.user_id,
        conversation_type=updated_conversation.conversation_type,
        status=updated_conversation.status,
        metadata=updated_conversation.metadata,
        message_count=len(updated_conversation.messages),
        created_at=updated_conversation.created_at,
        updated_at=updated_conversation.updated_at
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete conversation"""
    conversations_collection = await get_conversations_collection()
    
    # Check if conversation exists and belongs to user
    result = await conversations_collection.delete_one({
        "conversation_id": conversation_id,
        "user_id": current_user.user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    logger.info(f"Conversation deleted: {conversation_id}")
    
    return {"message": "Conversation deleted successfully"}


@router.post("/{conversation_id}/messages")
async def add_message_to_conversation(
    conversation_id: str,
    message_data: MessageCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """Add message to conversation"""
    conversations_collection = await get_conversations_collection()
    
    # Check if conversation exists and belongs to user
    conversation_doc = await conversations_collection.find_one({
        "conversation_id": conversation_id,
        "user_id": current_user.user_id
    })
    
    if not conversation_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create message
    message = {
        "message_id": f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
        "sender_type": message_data.sender_type,
        "content": message_data.content,
        "content_type": message_data.content_type,
        "timestamp": datetime.utcnow(),
        "metadata": message_data.metadata or {}
    }
    
    # Add message to conversation
    result = await conversations_collection.update_one(
        {"conversation_id": conversation_id},
        {
            "$push": {"messages": message},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    logger.info(f"Message added to conversation: {conversation_id}")
    
    return {"message": "Message added successfully", "message_id": message["message_id"]}


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(50, ge=1, le=500, description="Number of messages to retrieve"),
    current_user: User = Depends(get_current_user)
):
    """Get messages from conversation"""
    conversations_collection = await get_conversations_collection()
    
    # Use aggregation to get paginated messages
    pipeline = [
        {
            "$match": {
                "conversation_id": conversation_id,
                "user_id": current_user.user_id
            }
        },
        {
            "$project": {
                "messages": {
                    "$slice": ["$messages", skip, limit]
                }
            }
        }
    ]
    
    cursor = conversations_collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return {
        "conversation_id": conversation_id,
        "messages": result[0].get("messages", [])
    }


@router.get("/{conversation_id}/summary")
async def get_conversation_summary(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get conversation summary and statistics"""
    conversations_collection = await get_conversations_collection()
    
    # Use aggregation to get summary
    pipeline = [
        {
            "$match": {
                "conversation_id": conversation_id,
                "user_id": current_user.user_id
            }
        },
        {
            "$project": {
                "conversation_id": 1,
                "conversation_type": 1,
                "status": 1,
                "created_at": 1,
                "updated_at": 1,
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
                }
            }
        }
    ]
    
    cursor = conversations_collection.aggregate(pipeline)
    result = await cursor.to_list(length=1)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return result[0]
