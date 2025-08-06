from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.db.database import get_users_collection
from app.models import User
from app.schemas.user import UserResponse, UserUpdateRequest
from app.api.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to retrieve"),
    search: Optional[str] = Query(None, description="Search users by name or phone"),
    current_user: User = Depends(get_current_user)
):
    """Get list of users with pagination and search"""
    users_collection = await get_users_collection()
    
    # Build query
    query = {}
    if search:
        query["$or"] = [
            {"full_name": {"$regex": search, "$options": "i"}},
            {"phone_number": {"$regex": search, "$options": "i"}}
        ]
    
    # Get users
    cursor = users_collection.find(query).skip(skip).limit(limit)
    users = []
    
    async for user_doc in cursor:
        user = User(**user_doc)
        users.append(UserResponse(
            user_id=user.user_id,
            phone_number=user.phone_number,
            email=user.email,
            full_name=user.full_name,
            preferred_language=user.preferred_language,
            account_status=user.account_status,
            created_at=user.created_at
        ))
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user by ID"""
    users_collection = await get_users_collection()
    
    user_doc = await users_collection.find_one({"user_id": user_id})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    return UserResponse(
        user_id=user.user_id,
        phone_number=user.phone_number,
        email=user.email,
        full_name=user.full_name,
        preferred_language=user.preferred_language,
        account_status=user.account_status,
        created_at=user.created_at
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user)
):
    """Update user information"""
    # Check if user can update this profile (either own profile or admin)
    if user_id != current_user.user_id:
        # In a real app, you'd check for admin privileges here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user"
        )
    
    users_collection = await get_users_collection()
    
    # Check if user exists
    user_doc = await users_collection.find_one({"user_id": user_id})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Build update data
    update_data = {}
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.email is not None:
        update_data["email"] = user_update.email
    if user_update.preferred_language is not None:
        update_data["preferred_language"] = user_update.preferred_language
    if user_update.profile is not None:
        update_data["profile"] = user_update.profile
    if user_update.preferences is not None:
        update_data["preferences"] = user_update.preferences
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        
        # Update user
        result = await users_collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    
    # Get updated user
    updated_user_doc = await users_collection.find_one({"user_id": user_id})
    updated_user = User(**updated_user_doc)
    
    logger.info(f"User updated: {user_id}")
    
    return UserResponse(
        user_id=updated_user.user_id,
        phone_number=updated_user.phone_number,
        email=updated_user.email,
        full_name=updated_user.full_name,
        preferred_language=updated_user.preferred_language,
        account_status=updated_user.account_status,
        created_at=updated_user.created_at
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Deactivate user account (soft delete)"""
    # Check if user can delete this profile (either own profile or admin)
    if user_id != current_user.user_id:
        # In a real app, you'd check for admin privileges here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this user"
        )
    
    users_collection = await get_users_collection()
    
    # Soft delete by setting is_active to False
    result = await users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "account_status.is_active": False,
                "account_status.deactivated_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    logger.info(f"User deactivated: {user_id}")
    
    return {"message": "User account deactivated successfully"}


@router.get("/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user profile details"""
    users_collection = await get_users_collection()
    
    user_doc = await users_collection.find_one({"user_id": user_id})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = User(**user_doc)
    
    return {
        "user_id": user.user_id,
        "full_name": user.full_name,
        "profile": user.profile,
        "preferences": user.preferences,
        "preferred_language": user.preferred_language,
        "account_status": user.account_status
    }


@router.get("/{user_id}/login-history")
async def get_user_login_history(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user login history"""
    # Check if user can view this history (either own history or admin)
    if user_id != current_user.user_id:
        # In a real app, you'd check for admin privileges here
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user's login history"
        )
    
    users_collection = await get_users_collection()
    
    user_doc = await users_collection.find_one(
        {"user_id": user_id},
        {"login_history": 1}
    )
    
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "user_id": user_id,
        "login_history": user_doc.get("login_history", [])
    }
