from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Union
from enum import Enum
import uuid

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

class UsagePurpose(str, Enum):
    TRANSFUSION = "transfusion"
    EMERGENCY = "emergency"
    SURGERY = "surgery"
    TRANSFER = "transfer"

# ==================== BLOOD COLLECTION SCHEMAS ====================

class BloodCollectionBase(BaseModel):
    donor_id: str = Field(..., description="Donor identifier")
    donor_name: str = Field(..., min_length=2, max_length=200)
    donor_age: int = Field(..., ge=18, le=70, description="Donor age (18-70)")
    donor_gender: Gender
    donor_occupation: Optional[str] = Field(None, max_length=100)
    
    blood_type: BloodType
    collection_site: str = Field(..., max_length=200)
    donation_date: datetime
    expiry_date: datetime
    collection_volume_ml: float = Field(..., gt=0, le=500, description="Collection volume in ml")
    hemoglobin_g_dl: float = Field(..., gt=0, le=20, description="Hemoglobin level in g/dL")

class BloodCollectionCreate(BloodCollectionBase):
    pass

class BloodCollectionUpdate(BaseModel):
    donor_name: Optional[str] = Field(None, min_length=2, max_length=200)
    donor_occupation: Optional[str] = Field(None, max_length=100)
    collection_site: Optional[str] = Field(None, max_length=200)
    expiry_date: Optional[datetime] = None
    hemoglobin_g_dl: Optional[float] = Field(None, gt=0, le=20)

class BloodCollectionResponse(BloodCollectionBase):
    donation_record_id: Union[str, uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== BLOOD USAGE SCHEMAS ====================

class BloodUsageBase(BaseModel):
    purpose: UsagePurpose
    department: str = Field(..., max_length=100)
    blood_group: BloodType
    volume_given_out: float = Field(..., gt=0, le=500, description="Volume given out in ml")
    time: datetime
    individual_name: str = Field(..., min_length=2, max_length=200, description="Name of individual blood was given to")
    patient_location: str = Field(..., max_length=200, description="Hospital name where patient is located")

class BloodUsageCreate(BloodUsageBase):
    pass

class BloodUsageUpdate(BaseModel):
    purpose: Optional[UsagePurpose] = None
    department: Optional[str] = Field(None, max_length=100)
    individual_name: Optional[str] = Field(None, min_length=2, max_length=200)
    patient_location: Optional[str] = Field(None, max_length=200)

class BloodUsageResponse(BloodUsageBase):
    usage_id: Union[str, uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== BLOOD STOCK SCHEMAS ====================

class BloodStockBase(BaseModel):
    blood_group: BloodType
    volume_in_stock: float = Field(..., ge=0, description="Current stock volume in ml")
    time: datetime
    donation_record_id: Optional[Union[str, uuid.UUID]] = None
    usage_record_id: Optional[Union[str, uuid.UUID]] = None

class BloodStockCreate(BloodStockBase):
    pass

class BloodStockResponse(BloodStockBase):
    stock_id: Union[str, uuid.UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== INVENTORY ANALYTICS SCHEMAS ====================

class BloodInventorySummary(BaseModel):
    blood_group: BloodType
    current_volume_ml: float = Field(..., ge=0)
    available_units: int = Field(..., ge=0)
    last_updated: datetime

class InventoryAlert(BaseModel):
    blood_group: BloodType
    alert_type: str  # "low_stock", "expiring_soon", "expired"
    current_volume_ml: float
    threshold_volume_ml: float
    urgency_level: str  # "high", "medium", "low"
    message: str

# ==================== DHIS2 INTEGRATION SCHEMAS ====================

class DHIS2SyncRequest(BaseModel):
    entity_type: str = Field(..., description="Type of entity to sync (collections, usage, stock)")
    entity_ids: List[str] = Field(..., description="List of entity IDs to sync")
    sync_direction: str = Field(default="push", description="Sync direction: push, pull, or bidirectional")
    include_historical: bool = Field(default=False)

class DHIS2SyncResponse(BaseModel):
    total_records: int
    successful_syncs: int
    failed_syncs: int
    sync_timestamp: datetime
    failed_record_ids: List[str] = []
    error_messages: List[str] = []
