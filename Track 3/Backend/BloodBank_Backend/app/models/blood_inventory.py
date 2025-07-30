from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Index, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class BloodInventory(Base):
    """
    Blood Inventory/Stock Records
    Tracks current stock levels for each blood group with transaction history
    """
    __tablename__ = "blood_inventory"
    
    # Primary identification
    inventory_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Blood Group
    blood_group = Column(String(5), nullable=False, index=True)  # A+, A-, B+, B-, AB+, AB-, O+, O-
    
    # Current Stock Levels
    current_volume_ml = Column(Float, nullable=False, default=0.0)  # Current available volume
    current_units = Column(Integer, nullable=False, default=0)  # Current number of units
    reserved_volume_ml = Column(Float, default=0.0)  # Volume reserved for specific patients
    reserved_units = Column(Integer, default=0)  # Units reserved
    
    # Stock Thresholds
    minimum_stock_ml = Column(Float, default=2000.0)  # Minimum stock threshold
    maximum_stock_ml = Column(Float, default=10000.0)  # Maximum stock capacity
    reorder_point_ml = Column(Float, default=3000.0)  # Reorder trigger point
    
    # Transaction Details
    last_updated = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_transaction_type = Column(String(20))  # "donation", "usage", "adjustment", "expiry"
    last_transaction_volume = Column(Float)  # Last volume change (+ for addition, - for usage)
    
    # Related Transaction IDs (for tracking)
    related_donation_id = Column(String(50), ForeignKey("blood_donations.donation_record_id"), nullable=True)
    related_usage_id = Column(String(50), ForeignKey("blood_usage.usage_record_id"), nullable=True)
    
    # Expiry Tracking
    units_expiring_7_days = Column(Integer, default=0)  # Units expiring within 7 days
    units_expiring_14_days = Column(Integer, default=0)  # Units expiring within 14 days
    volume_expiring_7_days_ml = Column(Float, default=0.0)
    volume_expiring_14_days_ml = Column(Float, default=0.0)
    
    # Quality Metrics
    wastage_rate_percent = Column(Float, default=0.0)  # Monthly wastage rate
    turnover_rate_days = Column(Float, default=0.0)  # Average stock turnover in days
    shortage_incidents = Column(Integer, default=0)  # Number of shortage incidents
    
    # DHIS2 Integration
    dhis2_data_element = Column(String(100))  # DHIS2 data element for stock
    dhis2_org_unit = Column(String(100))
    dhis2_sync_status = Column(String(20), default="pending")
    dhis2_sync_timestamp = Column(DateTime)
    
    # Temperature and Storage
    storage_temperature_min = Column(Float, default=2.0)  # Celsius
    storage_temperature_max = Column(Float, default=6.0)  # Celsius
    current_storage_temp = Column(Float)
    
    # Staff and Audit
    updated_by_staff_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    related_donation = relationship("BloodDonation", foreign_keys=[related_donation_id])
    related_usage = relationship("BloodUsage", foreign_keys=[related_usage_id])
    updated_by = relationship("User", foreign_keys=[updated_by_staff_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_blood_group_updated', 'blood_group', 'last_updated'),
        Index('idx_stock_levels', 'blood_group', 'current_volume_ml'),
    )
    
    def __repr__(self):
        return f"<BloodInventory(blood_group={self.blood_group}, volume={self.current_volume_ml}ml, units={self.current_units})>"
    
    @property
    def is_below_minimum(self) -> bool:
        """Check if stock is below minimum threshold"""
        return self.current_volume_ml < self.minimum_stock_ml
    
    @property
    def is_at_reorder_point(self) -> bool:
        """Check if stock is at or below reorder point"""
        return self.current_volume_ml <= self.reorder_point_ml
    
    @property
    def stock_status(self) -> str:
        """Get current stock status"""
        if self.current_volume_ml <= 0:
            return "out_of_stock"
        elif self.is_below_minimum:
            return "critically_low"
        elif self.is_at_reorder_point:
            return "low"
        elif self.current_volume_ml >= self.maximum_stock_ml * 0.9:
            return "high"
        else:
            return "adequate"
    
    @property
    def available_volume_ml(self) -> float:
        """Get available volume (current - reserved)"""
        return max(0, self.current_volume_ml - self.reserved_volume_ml)
    
    @property
    def available_units(self) -> int:
        """Get available units (current - reserved)"""
        return max(0, self.current_units - self.reserved_units)


class BloodInventoryTransaction(Base):
    """
    Blood Inventory Transaction Log
    Detailed log of all stock movements for audit and tracking
    """
    __tablename__ = "blood_inventory_transactions"
    
    # Primary identification
    transaction_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_ref = Column(String(50), unique=True, index=True, nullable=False)
    
    # Transaction Details
    blood_group = Column(String(5), nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False, index=True)  # donation, usage, adjustment, expiry, transfer
    volume_change_ml = Column(Float, nullable=False)  # Positive for additions, negative for usage
    units_change = Column(Integer, nullable=False)
    
    # Previous and New Stock Levels
    previous_volume_ml = Column(Float, nullable=False)
    new_volume_ml = Column(Float, nullable=False)
    previous_units = Column(Integer, nullable=False)
    new_units = Column(Integer, nullable=False)
    
    # Related Records
    related_donation_id = Column(String(50), nullable=True)
    related_usage_id = Column(String(50), nullable=True)
    
    # Transaction Metadata
    transaction_date = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    notes = Column(Text)
    batch_number = Column(String(50))
    
    # Staff and Audit
    performed_by_staff_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by_staff_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    performed_by = relationship("User", foreign_keys=[performed_by_staff_id])
    verified_by = relationship("User", foreign_keys=[verified_by_staff_id])
    
    # Indexes
    __table_args__ = (
        Index('idx_blood_group_date_type', 'blood_group', 'transaction_date', 'transaction_type'),
        Index('idx_transaction_date', 'transaction_date'),
    )
    
    def __repr__(self):
        return f"<InventoryTransaction(ref={self.transaction_ref}, type={self.transaction_type}, volume_change={self.volume_change_ml}ml)>"
