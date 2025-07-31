from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging
import uuid

from app.models.blood_collection import BloodCollection
from app.models.blood_usage import BloodUsage
from app.models.blood_stock import BloodStock
from app.schemas.blood_bank import (
    BloodCollectionCreate, BloodCollectionUpdate,
    BloodUsageCreate, BloodUsageUpdate,
    BloodStockCreate
)

logger = logging.getLogger(__name__)

class BloodBankService:
    """
    Service layer for blood bank operations
    Handles business logic, inventory management, and data integration
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== COLLECTION MANAGEMENT ====================
    
    def create_collection(self, collection_data: BloodCollectionCreate, staff_id: int) -> BloodCollection:
        """
        Create new blood collection record and update stock
        """
        try:
            # Create collection record
            collection_dict = collection_data.dict()
            collection_dict['created_by'] = staff_id
            
            collection = BloodCollection(**collection_dict)
            
            self.db.add(collection)
            self.db.flush()  # Get the ID without committing
            
            # Update stock with the collection
            self._update_stock_from_collection(collection)
            
            self.db.commit()
            logger.info(f"Created blood collection {collection.donation_record_id}")
            return collection
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating collection: {e}")
            raise
    
    def get_collections(
        self, 
        blood_type: Optional[str] = None,
        collection_date_from: Optional[datetime] = None,
        collection_date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[BloodCollection]:
        """Get blood collection records with filtering"""
        query = self.db.query(BloodCollection)
        
        if blood_type:
            query = query.filter(BloodCollection.blood_type == blood_type)
        if collection_date_from:
            query = query.filter(BloodCollection.donation_date >= collection_date_from)
        if collection_date_to:
            query = query.filter(BloodCollection.donation_date <= collection_date_to)
        
        return query.offset(offset).limit(limit).all()
    
    def update_collection(self, donation_record_id: str, update_data: BloodCollectionUpdate, staff_id: int) -> BloodCollection:
        """Update collection record"""
        collection = self.db.query(BloodCollection).filter(
            BloodCollection.donation_record_id == donation_record_id
        ).first()
        
        if not collection:
            raise ValueError(f"Collection {donation_record_id} not found")
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(collection, field, value)
        
        collection.updated_at = datetime.utcnow()
        self.db.commit()
        
        return collection
    
    # ==================== USAGE MANAGEMENT ====================
    
    def create_usage(self, usage_data: BloodUsageCreate, staff_id: int) -> BloodUsage:
        """
        Create new blood usage record and update stock
        """
        try:
            # Check if sufficient stock available
            current_stock = self._get_current_stock_volume(usage_data.blood_group)
            if current_stock < usage_data.volume_given_out:
                raise ValueError(f"Insufficient stock for {usage_data.blood_group}. Available: {current_stock}ml, Requested: {usage_data.volume_given_out}ml")
            
            # Create usage record
            usage_dict = usage_data.dict()
            usage_dict['processed_by'] = staff_id
            
            usage = BloodUsage(**usage_dict)
            
            self.db.add(usage)
            self.db.flush()  # Get the ID without committing
            
            # Update stock with the usage
            self._update_stock_from_usage(usage)
            
            self.db.commit()
            logger.info(f"Created blood usage {usage.usage_id}")
            return usage
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating usage: {e}")
            raise
    
    def get_usage_records(
        self,
        blood_group: Optional[str] = None,
        usage_date_from: Optional[datetime] = None,
        usage_date_to: Optional[datetime] = None,
        patient_location: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[BloodUsage]:
        """Get blood usage records with filtering"""
        query = self.db.query(BloodUsage)
        
        if blood_group:
            query = query.filter(BloodUsage.blood_group == blood_group)
        if usage_date_from:
            query = query.filter(BloodUsage.time >= usage_date_from)
        if usage_date_to:
            query = query.filter(BloodUsage.time <= usage_date_to)
        if patient_location:
            query = query.filter(BloodUsage.patient_location.ilike(f"%{patient_location}%"))
        
        return query.offset(offset).limit(limit).all()
    
    # ==================== STOCK MANAGEMENT ====================
    
    def get_current_inventory(self) -> List[Dict[str, Any]]:
        """Get current inventory levels for all blood groups"""
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        inventory = []
        
        for blood_group in blood_groups:
            stock_data = self._get_current_stock_data(blood_group)
            
            inventory.append({
                "blood_group": blood_group,
                "total_available": stock_data["total_available"],
                "total_near_expiry": stock_data["total_near_expiry"],
                "total_expired": stock_data["total_expired"],
                "available_units": int(stock_data["total_available"] // 450),  # Assuming 450ml per unit
                "last_updated": stock_data["last_updated"]
            })
        
        return inventory
    
    def get_inventory_by_blood_group(self, blood_group: str) -> Dict[str, Any]:
        """Get inventory for specific blood group"""
        stock_data = self._get_current_stock_data(blood_group)
        
        return {
            "blood_group": blood_group,
            "total_available": stock_data["total_available"],
            "total_near_expiry": stock_data["total_near_expiry"],
            "total_expired": stock_data["total_expired"],
            "available_units": int(stock_data["total_available"] // 450),
            "last_updated": stock_data["last_updated"]
        }
    
    def _get_current_stock_data(self, blood_group: str) -> Dict[str, Any]:
        """Get current stock data for a blood group"""
        latest_stock = self.db.query(BloodStock).filter(
            BloodStock.blood_group == blood_group
        ).order_by(desc(BloodStock.stock_date)).first()
        
        if latest_stock:
            return {
                "total_available": latest_stock.total_available,
                "total_near_expiry": latest_stock.total_near_expiry,
                "total_expired": latest_stock.total_expired,
                "last_updated": latest_stock.updated_at
            }
        else:
            return {
                "total_available": 0.0,
                "total_near_expiry": 0.0,
                "total_expired": 0.0,
                "last_updated": datetime.utcnow()
            }
    
    # ==================== ALERTS AND MONITORING ====================
    
    def get_low_stock_alerts(self, threshold_ml: float = 1000.0) -> List[Dict[str, Any]]:
        """Get blood groups with low stock levels"""
        blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        alerts = []
        
        for blood_group in blood_groups:
            stock_data = self._get_current_stock_data(blood_group)
            current_volume = stock_data["total_available"]
            
            if current_volume < threshold_ml:
                alerts.append({
                    "blood_group": blood_group,
                    "current_volume_ml": current_volume,
                    "threshold_volume_ml": threshold_ml,
                    "urgency_level": "high" if current_volume < threshold_ml / 2 else "medium",
                    "message": f"Low stock alert: {blood_group} has only {current_volume}ml remaining"
                })
        
        return alerts
    
    def get_expiry_alerts(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Get blood units expiring within specified days"""
        cutoff_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        expiring_collections = self.db.query(BloodCollection).filter(
            BloodCollection.expiry_date <= cutoff_date,
            BloodCollection.expiry_date > datetime.utcnow()
        ).all()
        
        alerts = []
        for collection in expiring_collections:
            alerts.append({
                "donation_record_id": str(collection.donation_record_id),
                "blood_type": collection.blood_type,
                "volume_ml": collection.collection_volume_ml,
                "expiry_date": collection.expiry_date,
                "days_until_expiry": (collection.expiry_date - datetime.utcnow()).days,
                "donor_name": collection.donor_name
            })
        
        return alerts
    
    # ==================== ANALYTICS ====================
    
    def get_inventory_analytics(self, days_back: int = 30) -> Dict[str, Any]:
        """Get comprehensive inventory analytics"""
        start_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Current inventory
        current_inventory = self.get_current_inventory()
        
        # Collection analytics
        collections = self.db.query(BloodCollection).filter(
            BloodCollection.donation_date >= start_date
        ).all()
        
        collections_by_type = {}
        for collection in collections:
            blood_type = collection.blood_type
            if blood_type not in collections_by_type:
                collections_by_type[blood_type] = {"total_volume_ml": 0, "total_units": 0}
            collections_by_type[blood_type]["total_volume_ml"] += collection.collection_volume_ml
            collections_by_type[blood_type]["total_units"] += 1
        
        # Usage analytics
        usage_records = self.db.query(BloodUsage).filter(
            BloodUsage.time >= start_date
        ).all()
        
        usage_by_type = {}
        for usage in usage_records:
            blood_group = usage.blood_group
            if blood_group not in usage_by_type:
                usage_by_type[blood_group] = {"total_volume_ml": 0, "total_units": 0}
            usage_by_type[blood_group]["total_volume_ml"] += usage.volume_given_out
            usage_by_type[blood_group]["total_units"] += 1
        
        return {
            "period_days": days_back,
            "current_inventory": current_inventory,
            "collections": [{"blood_type": k, **v} for k, v in collections_by_type.items()],
            "usage": [{"blood_group": k, **v} for k, v in usage_by_type.items()]
        }
    
    # ==================== PRIVATE HELPER METHODS ====================
    
    def _update_stock_from_collection(self, collection: BloodCollection):
        """Update stock levels when blood is collected"""
        try:
            # Get or create current stock record for this blood group
            stock_record = self._get_or_create_current_stock(collection.blood_type)
            
            # Update total available with new collection
            stock_record.total_available += collection.collection_volume_ml
            
            # Update expiry categories based on expiry date
            self._update_expiry_categories(stock_record, collection.blood_type)
            
            # Set reference to collection
            stock_record.donation_record_id = collection.donation_record_id
            
            self.db.add(stock_record)
            logger.info(f"Updated stock for {collection.blood_type}: +{collection.collection_volume_ml}ml")
            
        except Exception as e:
            logger.error(f"Error updating stock from collection: {e}")
            raise
    
    def _update_stock_from_usage(self, usage: BloodUsage):
        """Update stock levels when blood is used"""
        try:
            # Get or create current stock record for this blood group
            stock_record = self._get_or_create_current_stock(usage.blood_group)
            
            # Deduct from total available
            if stock_record.total_available >= usage.volume_given_out:
                stock_record.total_available -= usage.volume_given_out
            else:
                raise ValueError(f"Insufficient stock for {usage.blood_group}. Available: {stock_record.total_available}ml, Requested: {usage.volume_given_out}ml")
            
            # Update expiry categories
            self._update_expiry_categories(stock_record, usage.blood_group)
            
            # Set reference to usage
            stock_record.usage_record_id = usage.usage_id
            
            self.db.add(stock_record)
            logger.info(f"Updated stock for {usage.blood_group}: -{usage.volume_given_out}ml")
            
        except Exception as e:
            logger.error(f"Error updating stock from usage: {e}")
            raise
    
    def _get_or_create_current_stock(self, blood_group: str) -> BloodStock:
        """Get current stock record or create new one for blood group"""
        from datetime import date
        
        today = date.today()
        
        # Try to get today's stock record
        stock_record = self.db.query(BloodStock).filter(
            and_(
                BloodStock.blood_group == blood_group,
                BloodStock.stock_date == today
            )
        ).first()
        
        if not stock_record:
            # Get latest stock record to carry forward totals
            latest_stock = self.db.query(BloodStock).filter(
                BloodStock.blood_group == blood_group
            ).order_by(desc(BloodStock.stock_date)).first()
            
            # Create new stock record for today
            stock_record = BloodStock(
                blood_group=blood_group,
                stock_date=today,
                total_available=latest_stock.total_available if latest_stock else 0.0,
                total_near_expiry=latest_stock.total_near_expiry if latest_stock else 0.0,
                total_expired=latest_stock.total_expired if latest_stock else 0.0
            )
        
        return stock_record
    
    def _update_expiry_categories(self, stock_record: BloodStock, blood_group: str):
        """Update near expiry and expired categories based on current collections"""
        from datetime import date, timedelta
        
        today = date.today()
        near_expiry_threshold = today + timedelta(days=7)  # 7 days warning
        
        # Query collections that are still in stock
        collections = self.db.query(BloodCollection).filter(
            BloodCollection.blood_type == blood_group
        ).all()
        
        total_near_expiry = 0.0
        total_expired = 0.0
        
        for collection in collections:
            # Check if this collection has been used up (simplified logic)
            if collection.expiry_date <= today:
                total_expired += collection.collection_volume_ml
            elif collection.expiry_date <= near_expiry_threshold:
                total_near_expiry += collection.collection_volume_ml
        
        stock_record.total_near_expiry = total_near_expiry
        stock_record.total_expired = total_expired
    
    def _get_current_stock_volume(self, blood_group: str) -> float:
        """Get current total available stock volume for a blood group"""
        latest_stock = self.db.query(BloodStock).filter(
            BloodStock.blood_group == blood_group
        ).order_by(desc(BloodStock.stock_date)).first()
        
        return latest_stock.total_available if latest_stock else 0.0
    
    def _get_last_stock_update(self, blood_group: str) -> Optional[datetime]:
        """Get timestamp of last stock update for a blood group"""
        latest_stock = self.db.query(BloodStock).filter(
            BloodStock.blood_group == blood_group
        ).order_by(desc(BloodStock.stock_date)).first()
        
        return latest_stock.created_at if latest_stock else None
