from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.schemas.patient import (
    PatientCreate, PatientLogin, Patient, LoginResponse,
    RefreshTokenRequest, RefreshTokenResponse
)
from app.services.patient_service import PatientService
from app.core.auth import get_current_patient
from app.db.database import get_db
from app.core.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/signup", 
             response_model=Patient, 
             status_code=status.HTTP_201_CREATED,
             summary="Register a new patient",
             description="Create a new patient account with phone number as unique identifier")
async def signup(patient: PatientCreate):
    """
    Register a new patient account.
    
    **Authentication Method:**
    - Phone number is used as the unique identifier for login
    - Email is optional but recommended for account recovery
    - Password must be at least 6 characters
    
    **Example request:**
    ```json
    {
        "full_name": "John Doe",
        "phone_number": "+237123456789",
        "email": "john.doe@example.com",
        "preferred_language": "en",
        "password": "SecurePass123"
    }
    ```
    
    **Returns:** Patient information (excluding password)
    
    **Errors:**
    - 400: Patient with phone number or email already exists
    - 422: Validation errors (missing fields, invalid format)
    """
    try:
        db_patient = await PatientService.create_patient(patient)
        return Patient(
            patient_id=str(db_patient.id),
            full_name=db_patient.full_name,
            phone_number=db_patient.phone_number,
            email=db_patient.email,
            preferred_language=db_patient.preferred_language,
            created_at=db_patient.created_at
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating patient account: {str(e)}"
        )

@router.post("/login", 
             response_model=LoginResponse,
             summary="Patient login",
             description="Authenticate patient and receive access tokens")
async def login(login_data: PatientLogin):
    """
    Authenticate a patient and receive access tokens.
    
    **Authentication:**
    - Uses phone_number as username
    - Returns JWT tokens for API access
    - Access token expires in 30 minutes
    - Refresh token expires in 7 days
    
    **Example request:**
    ```json
    {
        "phone_number": "+237123456789",
        "password": "SecurePass123"
    }
    ```
    
    **Example response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 1800,
        "patient": {
            "patient_id": "123e4567-e89b-12d3-a456-426614174000",
            "full_name": "John Doe",
            "phone_number": "+237123456789",
            "email": "john.doe@example.com",
            "preferred_language": "en"
        }
    }
    ```
    
    **Usage:**
    Include access_token in Authorization header: "Bearer {access_token}"
    
    **Errors:**
    - 401: Invalid phone number or password
    - 422: Validation errors
    """
    patient = await PatientService.authenticate_patient(login_data)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone number or password"
        )
    
    return PatientService.create_login_response(patient)

@router.post("/refresh",
             response_model=RefreshTokenResponse,
             summary="Refresh access token",
             description="Get new access token using refresh token")
async def refresh_token(refresh_request: RefreshTokenRequest):
    """
    Get new access token using refresh token.
    
    **Example request:**
    ```json
    {
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    
    **Example response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "expires_in": 1800
    }
    ```
    
    **Errors:**
    - 401: Invalid or expired refresh token
    """
    try:
        result = await PatientService.refresh_access_token(refresh_request.refresh_token)
        return RefreshTokenResponse(**result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in refresh_token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token"
        )

@router.get("/me",
            response_model=Patient,
            summary="Get patient profile by ID",
            description="Get patient profile using query parameter")
async def get_patient_profile(patient_id: str = Query(..., description="Patient ID")):
    """
    Get patient profile by ID (query parameter).
    
    **Query Parameters:**
    - patient_id: UUID of the patient
    
    **Response:** Patient object
    
    **Errors:**
    - 404: Patient not found
    """
    patient = await PatientService.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return Patient(
        patient_id=str(patient.id),
        full_name=patient.full_name,
        phone_number=patient.phone_number,
        email=patient.email,
        preferred_language=patient.preferred_language,
        created_at=patient.created_at
    )

@router.get("/patient/{patient_id}",
            response_model=Patient,
            summary="Get specific patient by ID",
            description="Get specific patient by ID (path parameter)")
async def get_patient_by_path_id(patient_id: str):
    """
    Get specific patient by ID (path parameter).
    
    **Path Parameters:**
    - patient_id: UUID of the patient
    
    **Response:** Patient object
    
    **Errors:**
    - 404: Patient not found
    """
    patient = await PatientService.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    return Patient(
        patient_id=str(patient.id),
        full_name=patient.full_name,
        phone_number=patient.phone_number,
        email=patient.email,
        preferred_language=patient.preferred_language,
        created_at=patient.created_at
    )

@router.get("/patient/",
            response_model=List[Patient],
            summary="List all patients",
            description="List all patients with pagination")
async def list_patients(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of patients to return"),
    offset: int = Query(0, ge=0, description="Number of patients to skip")
):
    """
    List all patients with pagination.
    
    **Query Parameters:**
    - limit: Maximum number of results (1-1000, default: 100)
    - offset: Number of results to skip (default: 0)
    
    **Response:** Array of Patient objects
    """
    try:
        from app.models.models import Patient as PatientModel
        
        # Get patients with pagination
        patients = await PatientModel.find().skip(offset).limit(limit).to_list()
        
        return [
            Patient(
                patient_id=str(patient.id),
                full_name=patient.full_name,
                phone_number=patient.phone_number,
                email=patient.email,
                preferred_language=patient.preferred_language,
                created_at=patient.created_at
            ) for patient in patients
        ]
        
    except Exception as e:
        logger.error(f"Error listing patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving patients"
        )

@router.delete("/patient/{patient_id}",
               summary="Delete patient account",
               description="Permanently delete patient account")
async def delete_patient(patient_id: str):
    """
    Permanently delete patient account.
    
    **Path Parameters:**
    - patient_id: UUID of the patient
    
    **Response:** Success confirmation
    
    **Errors:**
    - 404: Patient not found
    """
    try:
        from app.models.models import Patient as PatientModel
        
        patient = await PatientModel.find_one({"patient_id": patient_id})
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        await patient.delete()
        logger.info(f"Patient {patient_id} deleted successfully")
        
        return {"message": "Patient deleted successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error deleting patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting patient"
        )
