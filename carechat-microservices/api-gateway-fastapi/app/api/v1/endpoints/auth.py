from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.core.config import settings
from app.db.database import get_users_collection
from app.models import User, LoginHistory
from app.schemas.auth import UserRegistration, UserLogin, TokenResponse, LogoutResponse
from app.schemas.user import UserResponse
from app.api.deps import get_current_user

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(phone_number: str, password: str):
    """Authenticate user by phone number and password"""
    users_collection = await get_users_collection()
    
    user_doc = await users_collection.find_one({"phone_number": phone_number})
    if not user_doc:
        return False
    
    if not verify_password(password, user_doc["hashed_password"]):
        # Increment failed login attempts
        await users_collection.update_one(
            {"phone_number": phone_number},
            {
                "$inc": {"account_status.failed_login_attempts": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return False
    
    # Reset failed login attempts and update last login
    await users_collection.update_one(
        {"phone_number": phone_number},
        {
            "$set": {
                "account_status.failed_login_attempts": 0,
                "account_status.last_login": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return User(**user_doc)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegistration):
    """Register a new user"""
    users_collection = await get_users_collection()
    
    # Check if user already exists
    existing_user = await users_collection.find_one({
        "$or": [
            {"phone_number": user_data.phone_number},
            {"email": user_data.email} if user_data.email else {"phone_number": user_data.phone_number}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone number or email already exists"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user document
    user = User(
        phone_number=user_data.phone_number,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        preferred_language=user_data.preferred_language,
        profile=user_data.profile or {},
        preferences=user_data.preferences or {}
    )
    
    # Insert user
    user_dict = user.dict(by_alias=True, exclude_none=True)
    result = await users_collection.insert_one(user_dict)
    
    if not result.inserted_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    logger.info(f"New user registered: {user.user_id}")
    
    return UserResponse(
        user_id=user.user_id,
        phone_number=user.phone_number,
        email=user.email,
        full_name=user.full_name,
        preferred_language=user.preferred_language,
        account_status=user.account_status,
        created_at=user.created_at
    )


@router.post("/login")
async def login(phone_number: str, password: str):
    """Login user and return access token"""
    user = await authenticate_user(phone_number, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.account_status.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
        )
    
    # Check for too many failed attempts
    if user.account_status.failed_login_attempts >= 5:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account locked due to too many failed login attempts",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id, "phone_number": user.phone_number},
        expires_delta=access_token_expires
    )
    
    # Log login
    users_collection = await get_users_collection()
    await users_collection.update_one(
        {"user_id": user.user_id},
        {
            "$push": {
                "login_history": {
                    "timestamp": datetime.utcnow(),
                    "ip_address": "0.0.0.0",  # Would get from request in real implementation
                    "user_agent": "Unknown"  # Would get from request headers
                }
            }
        }
    )
    
    logger.info(f"User logged in: {user.user_id}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user_id": user.user_id,
        "full_name": user.full_name,
        "preferred_language": user.preferred_language
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (in a real implementation, you'd invalidate the token)"""
    logger.info(f"User logged out: {current_user.user_id}")
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        user_id=current_user.user_id,
        phone_number=current_user.phone_number,
        email=current_user.email,
        full_name=current_user.full_name,
        preferred_language=current_user.preferred_language,
        account_status=current_user.account_status,
        created_at=current_user.created_at
    )


@router.post("/verify-token")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if token is valid"""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    # Get user from database
    users_collection = await get_users_collection()
    user_doc = await users_collection.find_one({"user_id": user_id})
    
    if user_doc is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return {"valid": True, "user_id": user_id}
