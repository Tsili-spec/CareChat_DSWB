from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class BloodUsage(Base):
    """
    Blood Usage/Distribution Records
    Tracks blood units given to patients or transferred to other facilities
    """
    __tablename__ = "blood_usage"
    
    # Primary identification
    usage_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usage_record_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Blood Details
    blood_group = Column(String(5), nullable=False, index=True)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    volume_used_ml = Column(Float, nullable=False)  # Volume dispensed in milliliters
    units_used = Column(Integer, default=1)  # Number of blood units used
    
    # Recipient Information
    patient_name = Column(String(200))  # Can be anonymized for privacy
    patient_id = Column(String(50), index=True)  # Hospital patient ID
    patient_age = Column(Integer)
    patient_gender = Column(String(10))
    patient_diagnosis = Column(Text)  # Primary diagnosis requiring blood
    patient_department = Column(String(100))  # Emergency, Surgery, ICU, etc.
    
    # Usage Details
    usage_date = Column(DateTime, nullable=False, index=True)
    usage_reason = Column(String(100))  # Transfusion, Surgery, Emergency, etc.
    urgency_level = Column(String(20), default="routine")  # emergency, urgent, routine
    
    # Location and Transfer
    recipient_location = Column(String(200), nullable=False)  # Hospital name/location
    is_internal_usage = Column(Boolean, default=True)  # True for DGH, False for transfers
    transfer_destination = Column(String(200))  # Other hospital if transferred
    transfer_contact = Column(String(100))  # Contact person for transfers
    
    # Cross-matching and Compatibility
    crossmatch_performed = Column(Boolean, default=True)
    crossmatch_result = Column(String(20))  # Compatible, Incompatible, Pending
    crossmatch_by_staff_id = Column(Integer, ForeignKey("users.id"))
    
    # Source Blood Units (linking to donations)
    source_donation_ids = Column(Text)  # JSON array of donation_record_ids used
    bag_numbers_used = Column(Text)  # JSON array of bag numbers used
    
    # DHIS2 Integration
    dhis2_event_id = Column(String(100), unique=True)
    dhis2_org_unit = Column(String(100))
    dhis2_sync_status = Column(String(20), default="pending")
    dhis2_sync_timestamp = Column(DateTime)
    
    # Medical Authorization
    prescribed_by_doctor = Column(String(200))  # Doctor who prescribed
    doctor_license_number = Column(String(50))
    authorization_code = Column(String(50))
    
    # Quality and Safety
    pre_transfusion_checks = Column(Boolean, default=False)
    adverse_reactions = Column(Text)  # Any reported adverse reactions
    transfusion_outcome = Column(String(50))  # Successful, Adverse, Pending
    
    # Staff and Audit
    dispensed_by_staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by_staff_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    dispensed_by = relationship("User", foreign_keys=[dispensed_by_staff_id])
    verified_by = relationship("User", foreign_keys=[verified_by_staff_id])
    crossmatch_by = relationship("User", foreign_keys=[crossmatch_by_staff_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blood_group_date', 'blood_group', 'usage_date'),
        Index('idx_patient_usage', 'patient_id', 'usage_date'),
        Index('idx_location_date', 'recipient_location', 'usage_date'),
        Index('idx_urgency_date', 'urgency_level', 'usage_date'),
    )
    
    def __repr__(self):
        return f"<BloodUsage(record_id={self.usage_record_id}, blood_group={self.blood_group}, volume={self.volume_used_ml}ml)>"
    
    @property
    def source_donations_list(self) -> list:
        """Parse source donation IDs from JSON"""
        import json
        try:
            return json.loads(self.source_donation_ids) if self.source_donation_ids else []
        except:
            return []
    
    @property
    def bag_numbers_list(self) -> list:
        """Parse bag numbers from JSON"""
        import json
        try:
            return json.loads(self.bag_numbers_used) if self.bag_numbers_used else []
        except:
            return []
