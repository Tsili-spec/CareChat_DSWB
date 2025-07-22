from fastapi import APIRouter, Depends
from app.core.auth import get_current_patient, get_current_patient_optional
from app.models.user import User
from app.schemas.user import UserResponse
from typing import Optional

router = APIRouter(prefix="/protected", tags=["protected"])

@router.get("/profile", response_model=UserResponse)
async def get_protected_profile(current_patient: User = Depends(get_current_patient)):
    """Protected endpoint - requires authentication"""
    return UserResponse(
        patient_id=current_patient.patient_id,
        full_name=current_patient.full_name,
        phone_number=current_patient.phone_number,
        email=current_patient.email,
        preferred_language=current_patient.preferred_language
    )

@router.get("/optional-auth")
async def optional_auth_endpoint(current_patient: Optional[User] = Depends(get_current_patient_optional)):
    """Endpoint with optional authentication"""
    if current_patient:
        return {
            "message": f"Hello {current_patient.full_name}!",
            "authenticated": True,
            "patient_id": str(current_patient.patient_id)
        }
    else:
        return {
            "message": "Hello anonymous user!",
            "authenticated": False
        }
