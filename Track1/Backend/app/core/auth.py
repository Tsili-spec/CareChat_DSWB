from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.patient_service import PatientService
from app.models.models import Patient as PatientModel
from typing import Optional

# Security scheme for JWT Bearer token
security = HTTPBearer()

async def get_current_patient(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> PatientModel:
    """
    Dependency to get the current authenticated patient.
    
    **Usage in endpoints:**
    ```python
    @router.get("/protected-endpoint")
    def protected_route(current_patient: PatientModel = Depends(get_current_patient)):
        # Only authenticated patients can access this
        return {"patient_id": current_patient.patient_id}
    ```
    
    **Authentication:**
    - Requires "Authorization: Bearer {access_token}" header
    - Validates JWT token and returns patient object
    - Raises 401 if token is invalid/expired
    """
    token = credentials.credentials
    return PatientService.get_current_patient(db, token)

async def get_current_patient_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[PatientModel]:
    """
    Optional authentication dependency.
    Returns patient if authenticated, None if not.
    
    **Usage:**
    For endpoints that can work with or without authentication.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        return PatientService.get_current_patient(db, token)
    except HTTPException:
        return None 