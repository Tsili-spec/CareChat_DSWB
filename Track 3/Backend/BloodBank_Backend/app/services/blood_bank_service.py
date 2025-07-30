from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging

from app.models.blood_donation import BloodDonation
from app.models.blood_usage import BloodUsage
from app.models.blood_inventory import BloodInventory, BloodInventoryTransaction
from app.schemas.blood_bank import (
    BloodDonationCreate, BloodDonationUpdate,
    BloodUsageCreate, BloodUsageUpdate,
    BloodInventoryUpdate, InventoryTransactionCreate
)

logger = logging.getLogger(__name__)

class BloodBankService:
    """
    Service layer for blood bank operations
    Handles business logic, inventory management, and data integration
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== DONATION MANAGEMENT ====================
    
    def create_donation(self, donation_data: BloodDonationCreate, staff_id: int) -> BloodDonation:
        """
        Create new blood donation record and update inventory
        """
        try:
            # Create donation record
            donation_dict = donation_data.dict()
            donation_dict['collected_by_staff_id'] = staff_id  # Override with passed staff_id
            
            donation = BloodDonation(
                **donation_dict,
                screening_passed=self._evaluate_screening_results(donation_data),
                quality_check_passed=False  # Will be updated later
            )
            
            self.db.add(donation)
            self.db.flush()  # Get the ID without committing
            
            # Update inventory if screening passed
            if donation.screening_passed:
                self._update_inventory_from_donation(donation)
                
                # Create inventory transaction log
                self._create_inventory_transaction(
                    blood_group=donation.blood_type,
                    transaction_type="donation",
                    volume_change=donation.collection_volume_ml,
                    units_change=1,
                    related_donation_id=donation.donation_record_id,
                    staff_id=staff_id
                )
            
            self.db.commit()
            logger.info(f"Created donation record {donation.donation_record_id}")
            return donation
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating donation: {e}")
            raise
    
    def update_donation(self, donation_id: int, update_data: BloodDonationUpdate, staff_id: int) -> BloodDonation:
        """
        Update donation record and handle inventory changes
        """
        donation = self.db.query(BloodDonation).filter(BloodDonation.donation_id == donation_id).first()
        if not donation:
            raise ValueError(f"Donation {donation_id} not found")
        
        # Store original values for inventory adjustment
        original_screening = donation.screening_passed
        original_volume = donation.collection_volume_ml
        
        # Update donation fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(donation, field, value)
        
        donation.updated_at = datetime.utcnow()
        
        # Handle inventory adjustments if screening status changed
        if hasattr(update_data, 'screening_passed') and update_data.screening_passed != original_screening:
            if update_data.screening_passed and not original_screening:
                # Screening passed - add to inventory
                self._update_inventory_from_donation(donation)
            elif not update_data.screening_passed and original_screening:
                # Screening failed - remove from inventory
                self._adjust_inventory(
                    blood_group=donation.blood_type,
                    volume_change=-original_volume,
                    units_change=-1,
                    transaction_type="adjustment",
                    staff_id=staff_id,
                    notes=f"Screening failed for donation {donation.donation_record_id}"
                )
        
        self.db.commit()
        return donation
    
    def get_donations(self, 
                     blood_type: Optional[str] = None,
                     collection_date_from: Optional[datetime] = None,
                     collection_date_to: Optional[datetime] = None,
                     donor_id: Optional[str] = None,
                     processing_status: Optional[str] = None,
                     limit: int = 100,
                     offset: int = 0) -> List[BloodDonation]:
        """
        Get donations with filtering
        """
        query = self.db.query(BloodDonation)
        
        if blood_type:
            query = query.filter(BloodDonation.blood_type == blood_type)
        if collection_date_from:
            query = query.filter(BloodDonation.collection_date >= collection_date_from)
        if collection_date_to:
            query = query.filter(BloodDonation.collection_date <= collection_date_to)
        if donor_id:
            query = query.filter(BloodDonation.donor_id == donor_id)
        if processing_status:
            query = query.filter(BloodDonation.processing_status == processing_status)
        
        return query.offset(offset).limit(limit).all()
    
    # ==================== USAGE MANAGEMENT ====================
    
    def create_usage(self, usage_data: BloodUsageCreate, staff_id: int) -> BloodUsage:
        """
        Create blood usage record and update inventory
        """
        try:
            # Check inventory availability
            inventory = self._get_or_create_inventory(usage_data.blood_group)
            
            if inventory.available_volume_ml < usage_data.volume_used_ml:
                raise ValueError(f"Insufficient stock. Available: {inventory.available_volume_ml}ml, Requested: {usage_data.volume_used_ml}ml")
            
            # Create usage record
            usage_dict = usage_data.dict()
            usage_dict['dispensed_by_staff_id'] = staff_id  # Override with passed staff_id
            
            # Convert lists to JSON strings for database storage
            if usage_dict.get('source_donation_ids'):
                usage_dict['source_donation_ids'] = json.dumps(usage_dict['source_donation_ids'])
            if usage_dict.get('bag_numbers_used'):
                usage_dict['bag_numbers_used'] = json.dumps(usage_dict['bag_numbers_used'])
            
            usage = BloodUsage(**usage_dict)
            
            self.db.add(usage)
            self.db.flush()
            
            # Update inventory
            self._adjust_inventory(
                blood_group=usage.blood_group,
                volume_change=-usage.volume_used_ml,
                units_change=-usage.units_used,
                transaction_type="usage",
                related_usage_id=usage.usage_record_id,
                staff_id=staff_id
            )
            
            self.db.commit()
            logger.info(f"Created usage record {usage.usage_record_id}")
            return usage
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating usage: {e}")
            raise
    
    def get_usage_records(self,
                         blood_group: Optional[str] = None,
                         usage_date_from: Optional[datetime] = None,
                         usage_date_to: Optional[datetime] = None,
                         patient_id: Optional[str] = None,
                         recipient_location: Optional[str] = None,
                         limit: int = 100,
                         offset: int = 0) -> List[BloodUsage]:
        """
        Get usage records with filtering
        """
        query = self.db.query(BloodUsage)
        
        if blood_group:
            query = query.filter(BloodUsage.blood_group == blood_group)
        if usage_date_from:
            query = query.filter(BloodUsage.usage_date >= usage_date_from)
        if usage_date_to:
            query = query.filter(BloodUsage.usage_date <= usage_date_to)
        if patient_id:
            query = query.filter(BloodUsage.patient_id == patient_id)
        if recipient_location:
            query = query.filter(BloodUsage.recipient_location.ilike(f"%{recipient_location}%"))
        
        return query.order_by(BloodUsage.usage_date.desc()).offset(offset).limit(limit).all()
    
    # ==================== INVENTORY MANAGEMENT ====================
    
    def get_current_inventory(self) -> List[BloodInventory]:
        """
        Get current inventory for all blood groups
        """
        return self.db.query(BloodInventory).all()
    
    def get_inventory_by_blood_group(self, blood_group: str) -> Optional[BloodInventory]:
        """
        Get inventory for specific blood group
        """
        return self.db.query(BloodInventory).filter(BloodInventory.blood_group == blood_group).first()
    
    def update_inventory_settings(self, blood_group: str, update_data: BloodInventoryUpdate) -> BloodInventory:
        """
        Update inventory thresholds and settings
        """
        inventory = self._get_or_create_inventory(blood_group)
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(inventory, field, value)
        
        inventory.last_updated = datetime.utcnow()
        self.db.commit()
        
        return inventory
    
    def get_low_stock_alerts(self) -> List[Dict[str, Any]]:
        """
        Get blood groups with low stock levels
        """
        low_stock = self.db.query(BloodInventory).filter(
            or_(
                BloodInventory.current_volume_ml <= BloodInventory.minimum_stock_ml,
                BloodInventory.current_volume_ml <= BloodInventory.reorder_point_ml
            )
        ).all()
        
        alerts = []
        for inventory in low_stock:
            alerts.append({
                "blood_group": inventory.blood_group,
                "current_volume_ml": inventory.current_volume_ml,
                "minimum_stock_ml": inventory.minimum_stock_ml,
                "reorder_point_ml": inventory.reorder_point_ml,
                "stock_status": inventory.stock_status,
                "days_of_supply": self._calculate_days_of_supply(inventory),
                "recommendation": self._get_reorder_recommendation(inventory)
            })
        
        return alerts
    
    def get_expiry_alerts(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get blood units expiring within specified days
        """
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        expiring_donations = self.db.query(BloodDonation).filter(
            and_(
                BloodDonation.expiry_date <= cutoff_date,
                BloodDonation.expiry_date > datetime.utcnow(),
                BloodDonation.processing_status == "stored",
                BloodDonation.screening_passed == True
            )
        ).all()
        
        alerts = []
        for donation in expiring_donations:
            alerts.append({
                "donation_record_id": donation.donation_record_id,
                "blood_type": donation.blood_type,
                "volume_ml": donation.collection_volume_ml,
                "expiry_date": donation.expiry_date,
                "days_until_expiry": donation.days_until_expiry,
                "bag_number": donation.bag_number,
                "storage_location": donation.storage_location
            })
        
        return alerts
    
    # ==================== ANALYTICS AND REPORTING ====================
    
    def get_inventory_analytics(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Get inventory analytics for dashboard
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Current stock levels
        current_inventory = self.get_current_inventory()
        
        # Total collections in period
        total_collections = self.db.query(
            BloodDonation.blood_type,
            func.sum(BloodDonation.collection_volume_ml).label('total_volume'),
            func.count(BloodDonation.donation_id).label('total_units')
        ).filter(
            and_(
                BloodDonation.collection_date >= cutoff_date,
                BloodDonation.screening_passed == True
            )
        ).group_by(BloodDonation.blood_type).all()
        
        # Total usage in period
        total_usage = self.db.query(
            BloodUsage.blood_group,
            func.sum(BloodUsage.volume_used_ml).label('total_volume'),
            func.sum(BloodUsage.units_used).label('total_units')
        ).filter(
            BloodUsage.usage_date >= cutoff_date
        ).group_by(BloodUsage.blood_group).all()
        
        return {
            "period_days": days_back,
            "current_inventory": [
                {
                    "blood_group": inv.blood_group,
                    "current_volume_ml": inv.current_volume_ml,
                    "current_units": inv.current_units,
                    "stock_status": inv.stock_status,
                    "available_volume_ml": inv.available_volume_ml
                } for inv in current_inventory
            ],
            "collections": [
                {
                    "blood_type": item.blood_type,
                    "total_volume_ml": float(item.total_volume or 0),
                    "total_units": item.total_units
                } for item in total_collections
            ],
            "usage": [
                {
                    "blood_group": item.blood_group,
                    "total_volume_ml": float(item.total_volume or 0),
                    "total_units": int(item.total_units or 0)
                } for item in total_usage
            ]
        }
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    def _evaluate_screening_results(self, donation_data: BloodDonationCreate) -> bool:
        """
        Evaluate if all screening tests passed
        """
        test_results = [
            donation_data.hiv_test_result,
            donation_data.hepatitis_b_test,
            donation_data.hepatitis_c_test,
            donation_data.syphilis_test,
            donation_data.malaria_test
        ]
        
        # All non-null results must be "Negative"
        for result in test_results:
            if result and result != "Negative":
                return False
        
        # Check hemoglobin level (minimum 12.5 g/dL)
        if donation_data.hemoglobin_g_dl < 12.5:
            return False
        
        return True
    
    def _get_or_create_inventory(self, blood_group: str) -> BloodInventory:
        """
        Get existing inventory record or create new one
        """
        inventory = self.db.query(BloodInventory).filter(
            BloodInventory.blood_group == blood_group
        ).first()
        
        if not inventory:
            inventory = BloodInventory(
                blood_group=blood_group,
                current_volume_ml=0.0,
                current_units=0
            )
            self.db.add(inventory)
            self.db.flush()
        
        return inventory
    
    def _update_inventory_from_donation(self, donation: BloodDonation):
        """
        Update inventory when new donation is added
        """
        inventory = self._get_or_create_inventory(donation.blood_type)
        
        inventory.current_volume_ml += donation.collection_volume_ml
        inventory.current_units += 1
        inventory.last_updated = datetime.utcnow()
        inventory.last_transaction_type = "donation"
        inventory.last_transaction_volume = donation.collection_volume_ml
        inventory.related_donation_id = donation.donation_record_id
        inventory.related_usage_id = None
        
        # Update expiry tracking
        self._update_expiry_tracking(inventory)
    
    def _adjust_inventory(self, blood_group: str, volume_change: float, units_change: int,
                         transaction_type: str, staff_id: int, related_donation_id: str = None,
                         related_usage_id: str = None, notes: str = None):
        """
        Adjust inventory levels and create transaction log
        """
        inventory = self._get_or_create_inventory(blood_group)
        
        # Store previous values
        previous_volume = inventory.current_volume_ml
        previous_units = inventory.current_units
        
        # Update inventory
        inventory.current_volume_ml = max(0, inventory.current_volume_ml + volume_change)
        inventory.current_units = max(0, inventory.current_units + units_change)
        inventory.last_updated = datetime.utcnow()
        inventory.last_transaction_type = transaction_type
        inventory.last_transaction_volume = volume_change
        
        if related_donation_id:
            inventory.related_donation_id = related_donation_id
        if related_usage_id:
            inventory.related_usage_id = related_usage_id
        
        # Create transaction log
        self._create_inventory_transaction(
            blood_group=blood_group,
            transaction_type=transaction_type,
            volume_change=volume_change,
            units_change=units_change,
            previous_volume=previous_volume,
            new_volume=inventory.current_volume_ml,
            previous_units=previous_units,
            new_units=inventory.current_units,
            related_donation_id=related_donation_id,
            related_usage_id=related_usage_id,
            staff_id=staff_id,
            notes=notes
        )
        
        # Update expiry tracking
        self._update_expiry_tracking(inventory)
    
    def _create_inventory_transaction(self, blood_group: str, transaction_type: str,
                                    volume_change: float, units_change: int,
                                    staff_id: int, related_donation_id: str = None,
                                    related_usage_id: str = None, previous_volume: float = None,
                                    new_volume: float = None, previous_units: int = None,
                                    new_units: int = None, notes: str = None):
        """
        Create inventory transaction log entry
        """
        import uuid
        
        # Generate transaction reference
        transaction_ref = f"{transaction_type.upper()}-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Get current inventory if previous values not provided
        if previous_volume is None or new_volume is None:
            inventory = self._get_or_create_inventory(blood_group)
            previous_volume = inventory.current_volume_ml - volume_change
            new_volume = inventory.current_volume_ml
            previous_units = inventory.current_units - units_change
            new_units = inventory.current_units
        
        transaction = BloodInventoryTransaction(
            transaction_ref=transaction_ref,
            blood_group=blood_group,
            transaction_type=transaction_type,
            volume_change_ml=volume_change,
            units_change=units_change,
            previous_volume_ml=previous_volume,
            new_volume_ml=new_volume,
            previous_units=previous_units,
            new_units=new_units,
            related_donation_id=related_donation_id,
            related_usage_id=related_usage_id,
            performed_by_staff_id=staff_id,
            notes=notes
        )
        
        self.db.add(transaction)
    
    def _update_expiry_tracking(self, inventory: BloodInventory):
        """
        Update expiry tracking for inventory
        """
        cutoff_7_days = datetime.utcnow() + timedelta(days=7)
        cutoff_14_days = datetime.utcnow() + timedelta(days=14)
        
        # Count units expiring within 7 and 14 days
        expiring_7 = self.db.query(BloodDonation).filter(
            and_(
                BloodDonation.blood_type == inventory.blood_group,
                BloodDonation.expiry_date <= cutoff_7_days,
                BloodDonation.expiry_date > datetime.utcnow(),
                BloodDonation.processing_status == "stored",
                BloodDonation.screening_passed == True
            )
        ).all()
        
        expiring_14 = self.db.query(BloodDonation).filter(
            and_(
                BloodDonation.blood_type == inventory.blood_group,
                BloodDonation.expiry_date <= cutoff_14_days,
                BloodDonation.expiry_date > datetime.utcnow(),
                BloodDonation.processing_status == "stored",
                BloodDonation.screening_passed == True
            )
        ).all()
        
        inventory.units_expiring_7_days = len(expiring_7)
        inventory.volume_expiring_7_days_ml = sum(d.collection_volume_ml for d in expiring_7)
        inventory.units_expiring_14_days = len(expiring_14)
        inventory.volume_expiring_14_days_ml = sum(d.collection_volume_ml for d in expiring_14)
    
    def _calculate_days_of_supply(self, inventory: BloodInventory) -> float:
        """
        Calculate days of supply based on recent usage patterns
        """
        # Get average daily usage over last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        avg_daily_usage = self.db.query(
            func.avg(BloodUsage.volume_used_ml).label('avg_daily')
        ).filter(
            and_(
                BloodUsage.blood_group == inventory.blood_group,
                BloodUsage.usage_date >= cutoff_date
            )
        ).scalar()
        
        if avg_daily_usage and avg_daily_usage > 0:
            return inventory.available_volume_ml / float(avg_daily_usage)
        else:
            return float('inf')  # No usage history
    
    def _get_reorder_recommendation(self, inventory: BloodInventory) -> str:
        """
        Get reorder recommendation based on stock levels and usage patterns
        """
        days_of_supply = self._calculate_days_of_supply(inventory)
        
        if inventory.current_volume_ml <= 0:
            return "URGENT: Out of stock - Emergency procurement needed"
        elif inventory.is_below_minimum:
            return f"CRITICAL: Below minimum stock ({days_of_supply:.1f} days supply) - Immediate reorder required"
        elif inventory.is_at_reorder_point:
            return f"WARNING: At reorder point ({days_of_supply:.1f} days supply) - Schedule procurement"
        else:
            return f"ADEQUATE: Stock sufficient ({days_of_supply:.1f} days supply)"
