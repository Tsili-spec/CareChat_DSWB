from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base

class BloodUsage(Base):
    """Blood usage/distribution records"""
    __tablename__ = "blood_usage"
    
    # Primary key - UUID as specified
    usage_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Transaction details - moved from blood_stock as requested
    purpose = Column(String(50), nullable=False)  # 'transfusion', 'emergency', 'surgery', 'transfer'
    department = Column(String(100), nullable=False)
    
    # Blood information
    blood_group = Column(String(10), nullable=False, index=True)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    volume_given_out = Column(Float, nullable=False)  # renamed as specified
    
    # Date - date only (no time except for audit columns)
    usage_date = Column(Date, nullable=False, index=True, server_default=func.current_date())
    
    # Patient/recipient information
    individual_name = Column(String(200), nullable=False)  # name of individual blood was given to
    patient_location = Column(String(200), nullable=False)  # hospital name (Douala General Hospital, etc.)
    
    # Audit fields
    processed_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'), nullable=True)
    
    # Audit timestamps (keep datetime for audit purposes)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    stock_entries = relationship("BloodStock", back_populates="usage")
    processed_by_user = relationship("User", foreign_keys=[processed_by])
    
    def __repr__(self):
        return f"<BloodUsage(id={self.usage_id}, blood_group={self.blood_group}, volume={self.volume_given_out}ml)>"
