from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.jwt_auth import JWTManager
from typing import Optional

# Security scheme for Bearer token
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    
    Args:
        credentials: Bearer token from request header
        db: Database session
        
    Returns:
        Current authenticated user object
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    # Verify token and extract payload
    token_data = JWTManager.verify_token(token)
    
    # Get user from database
    user = db.query(User).filter(
        User.username == token_data["username"]
    ).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to get current active user
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Optional: For routes that may or may not require authentication
def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency for optional authentication
    Returns None if no token provided, User if valid token
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

def require_role(required_role: str):
    """
    Dependency factory for role-based access control
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function that checks user role
    """
    def check_role(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        return current_user
    
    return check_role

def require_permission(permission: str):
    """
    Dependency factory for permission-based access control
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function that checks user permission
    """
    def check_permission(current_user: User = Depends(get_current_user)) -> User:
        # Check if user has the specific permission
        if not hasattr(current_user, permission) or not getattr(current_user, permission):
            if current_user.role != "admin":  # Admins have all permissions
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required permission: {permission}"
                )
        return current_user
    
    return check_permission
