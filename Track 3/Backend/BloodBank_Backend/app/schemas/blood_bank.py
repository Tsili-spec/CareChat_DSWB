from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

# Enums for validation
class BloodType(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "Other"

class TestResult(str, Enum):
    NEGATIVE = "Negative"
    POSITIVE = "Positive"
    PENDING = "Pending"

class ProcessingStatus(str, Enum):
    COLLECTED = "collected"
    PROCESSED = "processed"
    STORED = "stored"
    EXPIRED = "expired"

class UrgencyLevel(str, Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent"
    ROUTINE = "routine"

# Blood Donation Schemas
class BloodDonationBase(BaseModel):
    donation_record_id: str = Field(..., description="External system donation ID")
    donor_id: str = Field(..., description="DHIS2 donor ID")
    donor_name: str = Field(..., min_length=2, max_length=200)
    donor_age: int = Field(..., ge=18, le=65, description="Donor age (18-65)")
    donor_gender: Gender
    donor_occupation: Optional[str] = Field(None, max_length=100)
    donor_phone: Optional[str] = Field(None, max_length=20)
    donor_address: Optional[str] = None
    
    blood_type: BloodType
    collection_volume_ml: float = Field(..., gt=0, le=500, description="Collection volume in ml")
    collection_site: str = Field(..., min_length=2, max_length=100)
    collection_date: datetime
    expiry_date: datetime
    
    hemoglobin_g_dl: float = Field(..., ge=8.0, le=20.0, description="Hemoglobin level")
    blood_pressure_systolic: Optional[int] = Field(None, ge=80, le=200)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=50, le=120)
    temperature_celsius: Optional[float] = Field(None, ge=35.0, le=42.0)
    pulse_rate: Optional[int] = Field(None, ge=50, le=120)
    
    # Test results
    hiv_test_result: Optional[TestResult] = None
    hepatitis_b_test: Optional[TestResult] = None
    hepatitis_c_test: Optional[TestResult] = None
    syphilis_test: Optional[TestResult] = None
    malaria_test: Optional[TestResult] = None
    
    bag_number: Optional[str] = Field(None, max_length=50)
    storage_location: Optional[str] = Field(None, max_length=100)
    
    # DHIS2 fields
    dhis2_event_id: Optional[str] = None
    dhis2_org_unit: Optional[str] = None
    
    @validator('expiry_date')
    def expiry_must_be_after_collection(cls, v, values):
        if 'collection_date' in values and v <= values['collection_date']:
            raise ValueError('Expiry date must be after collection date')
        return v

class BloodDonationCreate(BloodDonationBase):
    collected_by_staff_id: int

class BloodDonationUpdate(BaseModel):
    processing_status: Optional[ProcessingStatus] = None
    quality_check_passed: Optional[bool] = None
    quality_notes: Optional[str] = None
    storage_temperature: Optional[float] = None
    processed_by_staff_id: Optional[int] = None

class BloodDonationResponse(BloodDonationBase):
    donation_id: int
    processing_status: ProcessingStatus
    screening_passed: bool
    quality_check_passed: bool
    is_expired: bool
    days_until_expiry: int
    is_near_expiry: bool
    dhis2_sync_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Blood Usage Schemas
class BloodUsageBase(BaseModel):
    usage_record_id: str = Field(..., description="Usage record ID")
    blood_group: BloodType
    volume_used_ml: float = Field(..., gt=0, description="Volume used in ml")
    units_used: int = Field(1, gt=0, description="Number of units used")
    
    patient_name: Optional[str] = Field(None, max_length=200)
    patient_id: Optional[str] = Field(None, max_length=50)
    patient_age: Optional[int] = Field(None, ge=0, le=120)
    patient_gender: Optional[Gender] = None
    patient_diagnosis: Optional[str] = None
    patient_department: Optional[str] = Field(None, max_length=100)
    
    usage_date: datetime
    usage_reason: Optional[str] = Field(None, max_length=100)
    urgency_level: UrgencyLevel = UrgencyLevel.ROUTINE
    
    recipient_location: str = Field(..., min_length=2, max_length=200)
    is_internal_usage: bool = True
    transfer_destination: Optional[str] = Field(None, max_length=200)
    transfer_contact: Optional[str] = Field(None, max_length=100)
    
    prescribed_by_doctor: Optional[str] = Field(None, max_length=200)
    doctor_license_number: Optional[str] = Field(None, max_length=50)
    authorization_code: Optional[str] = Field(None, max_length=50)
    
    source_donation_ids: Optional[List[str]] = Field(None, description="List of source donation IDs")
    bag_numbers_used: Optional[List[str]] = Field(None, description="List of bag numbers used")
    
    # DHIS2 fields
    dhis2_event_id: Optional[str] = None
    dhis2_org_unit: Optional[str] = None

class BloodUsageCreate(BloodUsageBase):
    dispensed_by_staff_id: int

class BloodUsageUpdate(BaseModel):
    crossmatch_result: Optional[str] = None
    crossmatch_by_staff_id: Optional[int] = None
    adverse_reactions: Optional[str] = None
    transfusion_outcome: Optional[str] = None
    verified_by_staff_id: Optional[int] = None

class BloodUsageResponse(BloodUsageBase):
    usage_id: int
    crossmatch_performed: bool
    crossmatch_result: Optional[str]
    pre_transfusion_checks: bool
    transfusion_outcome: Optional[str]
    dhis2_sync_status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Blood Inventory Schemas
class BloodInventoryBase(BaseModel):
    blood_group: BloodType
    current_volume_ml: float = Field(..., ge=0)
    current_units: int = Field(..., ge=0)
    reserved_volume_ml: float = Field(0, ge=0)
    reserved_units: int = Field(0, ge=0)
    minimum_stock_ml: float = Field(2000.0, gt=0)
    maximum_stock_ml: float = Field(10000.0, gt=0)
    reorder_point_ml: float = Field(3000.0, gt=0)

class BloodInventoryUpdate(BaseModel):
    minimum_stock_ml: Optional[float] = Field(None, gt=0)
    maximum_stock_ml: Optional[float] = Field(None, gt=0)
    reorder_point_ml: Optional[float] = Field(None, gt=0)
    current_storage_temp: Optional[float] = Field(None, ge=-10, le=10)

class BloodInventoryResponse(BloodInventoryBase):
    inventory_id: int
    is_below_minimum: bool
    is_at_reorder_point: bool
    stock_status: str
    available_volume_ml: float
    available_units: int
    units_expiring_7_days: int
    units_expiring_14_days: int
    volume_expiring_7_days_ml: float
    volume_expiring_14_days_ml: float
    wastage_rate_percent: float
    turnover_rate_days: float
    last_updated: datetime
    last_transaction_type: Optional[str]
    dhis2_sync_status: str
    
    class Config:
        from_attributes = True

# Transaction Schemas
class InventoryTransactionBase(BaseModel):
    blood_group: BloodType
    transaction_type: str = Field(..., description="donation, usage, adjustment, expiry, transfer")
    volume_change_ml: float = Field(..., description="Positive for additions, negative for usage")
    units_change: int = Field(..., description="Positive for additions, negative for usage")
    notes: Optional[str] = None
    batch_number: Optional[str] = None

class InventoryTransactionCreate(InventoryTransactionBase):
    performed_by_staff_id: int
    related_donation_id: Optional[str] = None
    related_usage_id: Optional[str] = None

class InventoryTransactionResponse(InventoryTransactionBase):
    transaction_id: int
    transaction_ref: str
    previous_volume_ml: float
    new_volume_ml: float
    previous_units: int
    new_units: int
    transaction_date: datetime
    
    class Config:
        from_attributes = True

# DHIS2 Integration Schemas
class DHIS2SyncRequest(BaseModel):
    entity_type: str = Field(..., description="donation, usage, inventory")
    entity_ids: List[int] = Field(..., description="List of record IDs to sync")
    org_unit: str = Field(..., description="DHIS2 organization unit")
    force_resync: bool = False

class DHIS2SyncResponse(BaseModel):
    total_records: int
    successful_syncs: int
    failed_syncs: int
    sync_timestamp: datetime
    failed_record_ids: List[int]
    error_messages: List[str]
