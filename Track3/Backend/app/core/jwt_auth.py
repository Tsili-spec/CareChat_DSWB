from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.core.config import settings

class JWTManager:
    """JWT token management utilities"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a new JWT access token
        
        Args:
            data: Payload data to encode in token
            expires_delta: Token expiration time (optional)
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create a new JWT refresh token
        
        Args:
            data: Payload data to encode in token
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)  # Refresh tokens last 30 days
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.JWT_REFRESH_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # First try with JWT_SECRET_KEY (for access tokens)
            try:
                payload = jwt.decode(
                    token, 
                    settings.JWT_SECRET_KEY, 
                    algorithms=[settings.ALGORITHM]
                )
            except JWTError:
                # If that fails, try with JWT_REFRESH_SECRET_KEY (for refresh tokens)
                payload = jwt.decode(
                    token, 
                    settings.JWT_REFRESH_SECRET_KEY, 
                    algorithms=[settings.ALGORITHM]
                )
            
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if username is None or user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return {
                "username": username,
                "user_id": user_id,
                "exp": payload.get("exp"),
                "type": payload.get("type")
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_token_expiry_time() -> int:
        """Get token expiration time in seconds"""
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Simple decode method for admin middleware
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            JWTError: If token is invalid or expired
        """
        return jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
