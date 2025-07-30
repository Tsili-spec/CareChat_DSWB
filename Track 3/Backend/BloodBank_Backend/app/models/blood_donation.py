from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class BloodDonation(Base):
    """
    Blood Collection/Donation Records
    Tracks all blood donations from donors with comprehensive metadata
    """
    __tablename__ = "blood_donations"
    
    # Primary identification
    donation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    donation_record_id = Column(String(50), unique=True, index=True, nullable=False)  # External system ID
    
    # Donor Information
    donor_id = Column(String(50), index=True, nullable=False)  # DHIS2 donor ID
    donor_name = Column(String(200), nullable=False)
    donor_age = Column(Integer, nullable=False)
    donor_gender = Column(String(10), nullable=False)  # M, F, Other
    donor_occupation = Column(String(100))
    donor_phone = Column(String(20))
    donor_address = Column(Text)
    
    # Blood Collection Details
    blood_type = Column(String(5), nullable=False, index=True)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    collection_volume_ml = Column(Float, nullable=False)  # Volume in milliliters
    collection_site = Column(String(100), nullable=False)  # Collection location
    collection_date = Column(DateTime, nullable=False, index=True)
    expiry_date = Column(DateTime, nullable=False, index=True)
    
    # Medical/Quality Data
    hemoglobin_g_dl = Column(Float, nullable=False)  # Hemoglobin level
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    temperature_celsius = Column(Float)
    pulse_rate = Column(Integer)
    
    # Screening Results
    hiv_test_result = Column(String(20))  # Negative, Positive, Pending
    hepatitis_b_test = Column(String(20))
    hepatitis_c_test = Column(String(20))
    syphilis_test = Column(String(20))
    malaria_test = Column(String(20))
    screening_passed = Column(Boolean, default=False)
    
    # Storage and Processing
    bag_number = Column(String(50), unique=True)
    processing_status = Column(String(30), default="collected")  # collected, processed, stored, expired
    storage_location = Column(String(100))
    storage_temperature = Column(Float)
    
    # DHIS2 Integration
    dhis2_event_id = Column(String(100), unique=True)  # DHIS2 event reference
    dhis2_org_unit = Column(String(100))  # DHIS2 organization unit
    dhis2_sync_status = Column(String(20), default="pending")  # pending, synced, failed
    dhis2_sync_timestamp = Column(DateTime)
    
    # Quality Assurance
    quality_check_passed = Column(Boolean, default=False)
    quality_notes = Column(Text)
    
    # Staff and Audit
    collected_by_staff_id = Column(Integer, ForeignKey("users.id"))
    processed_by_staff_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    collected_by = relationship("User", foreign_keys=[collected_by_staff_id])
    processed_by = relationship("User", foreign_keys=[processed_by_staff_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blood_type_date', 'blood_type', 'collection_date'),
        Index('idx_donor_collection', 'donor_id', 'collection_date'),
        Index('idx_expiry_status', 'expiry_date', 'processing_status'),
    )
    
    def __repr__(self):
        return f"<BloodDonation(record_id={self.donation_record_id}, blood_type={self.blood_type}, volume={self.collection_volume_ml}ml)>"
    
    @property
    def is_expired(self) -> bool:
        """Check if blood unit has expired"""
        from datetime import datetime
        return datetime.utcnow() > self.expiry_date
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until expiry"""
        from datetime import datetime
        delta = self.expiry_date - datetime.utcnow()
        return delta.days if delta.days > 0 else 0
    
    @property
    def is_near_expiry(self) -> bool:
        """Check if blood unit is near expiry (within 7 days)"""
        return 0 < self.days_until_expiry <= 7
