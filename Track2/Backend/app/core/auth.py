# Authentication middleware for protected endpoints
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.models.user import User
from app.core.jwt_auth import verify_token

security = HTTPBearer()

async def get_current_patient(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Required authentication - raises 401 if not authenticated"""
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    patient_id: str = payload.get("sub")
    if patient_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    patient = db.query(User).filter(User.patient_id == patient_id).first()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return patient

async def get_current_patient_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Optional authentication - returns None if not authenticated"""
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if payload is None:
        return None
    
    patient_id: str = payload.get("sub")
    if patient_id is None:
        return None
    
    patient = db.query(User).filter(User.patient_id == patient_id).first()
    return patient
