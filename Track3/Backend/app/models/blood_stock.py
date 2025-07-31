from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.database import Base

class BloodStock(Base):
    """Blood stock tracking with audit trail - Total volume table"""
    __tablename__ = "blood_stock"
    
    # Primary key - UUID as specified (only one primary key needed)
    stock_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Blood information
    blood_group = Column(String(10), nullable=False, index=True)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    
    # Stock volumes
    total_available = Column(Float, nullable=False, default=0.0)  # current total volume available
    total_near_expiry = Column(Float, nullable=False, default=0.0)  # volume near expiry (within 7 days)
    total_expired = Column(Float, nullable=False, default=0.0)  # volume expired
    
    # Date - date only (no time except for audit columns)
    stock_date = Column(Date, nullable=False, server_default=func.current_date(), index=True)
    
    # Foreign keys to track source/destination (nullable as specified)
    donation_record_id = Column(UUID(as_uuid=True), ForeignKey('blood_collections.donation_record_id'), nullable=True)
    usage_record_id = Column(UUID(as_uuid=True), ForeignKey('blood_usage.usage_id'), nullable=True)
    
    # Audit timestamps (keep datetime for audit purposes)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    collection = relationship("BloodCollection", back_populates="stock_entries")
    usage = relationship("BloodUsage", back_populates="stock_entries")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blood_stock_blood_group_date', 'blood_group', 'stock_date'),
        Index('idx_blood_stock_donation_ref', 'donation_record_id'),
        Index('idx_blood_stock_usage_ref', 'usage_record_id'),
    )
    
    def __repr__(self):
        return f"<BloodStock(id={self.stock_id}, blood_group={self.blood_group}, total_available={self.total_available}ml)>"
