from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.core.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.blood_bank import (
    BloodDonationCreate, BloodDonationUpdate, BloodDonationResponse,
    BloodUsageCreate, BloodUsageUpdate, BloodUsageResponse,
    BloodInventoryUpdate, BloodInventoryResponse,
    InventoryTransactionResponse, DHIS2SyncRequest, DHIS2SyncResponse
)
from app.services.blood_bank_service import BloodBankService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/blood-bank", tags=["Blood Bank Management"])

# ==================== DONATION ENDPOINTS ====================

@router.post("/donations", response_model=BloodDonationResponse, status_code=status.HTTP_201_CREATED)
def create_donation(
    donation_data: BloodDonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_donors"))
):
    """
    Create a new blood donation record
    
    Requires: can_manage_donors permission
    """
    try:
        service = BloodBankService(db)
        donation = service.create_donation(donation_data, current_user.id)
        return donation
    except Exception as e:
        logger.error(f"Error creating donation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create donation: {str(e)}"
        )

@router.get("/donations", response_model=List[BloodDonationResponse])
def get_donations(
    blood_type: Optional[str] = Query(None, description="Filter by blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)"),
    collection_date_from: Optional[datetime] = Query(None, description="Filter donations from this date"),
    collection_date_to: Optional[datetime] = Query(None, description="Filter donations up to this date"),
    donor_id: Optional[str] = Query(None, description="Filter by donor ID"),
    processing_status: Optional[str] = Query(None, description="Filter by processing status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_view_analytics"))
):
    """
    Get blood donation records with filtering
    
    Requires: can_view_analytics permission
    """
    service = BloodBankService(db)
    donations = service.get_donations(
        blood_type=blood_type,
        collection_date_from=collection_date_from,
        collection_date_to=collection_date_to,
        donor_id=donor_id,
        processing_status=processing_status,
        limit=limit,
        offset=offset
    )
    return donations

@router.get("/donations/{donation_id}", response_model=BloodDonationResponse)
def get_donation(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_view_analytics"))
):
    """
    Get specific donation record by ID
    
    Requires: can_view_analytics permission
    """
    from app.models.blood_donation import BloodDonation
    
    donation = db.query(BloodDonation).filter(BloodDonation.donation_id == donation_id).first()
    if not donation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Donation {donation_id} not found"
        )
    return donation

@router.put("/donations/{donation_id}", response_model=BloodDonationResponse)
def update_donation(
    donation_id: int,
    update_data: BloodDonationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_donors"))
):
    """
    Update donation record
    
    Requires: can_manage_donors permission
    """
    try:
        service = BloodBankService(db)
        donation = service.update_donation(donation_id, update_data, current_user.id)
        return donation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating donation {donation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update donation: {str(e)}"
        )

# ==================== USAGE ENDPOINTS ====================

@router.post("/usage", response_model=BloodUsageResponse, status_code=status.HTTP_201_CREATED)
def create_usage(
    usage_data: BloodUsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_inventory"))
):
    """
    Record blood usage/distribution
    
    Requires: can_manage_inventory permission
    """
    try:
        service = BloodBankService(db)
        usage = service.create_usage(usage_data, current_user.id)
        return usage
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating usage record: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create usage record: {str(e)}"
        )

@router.get("/usage", response_model=List[BloodUsageResponse])
def get_usage_records(
    blood_group: Optional[str] = Query(None, description="Filter by blood group"),
    usage_date_from: Optional[datetime] = Query(None, description="Filter usage from this date"),
    usage_date_to: Optional[datetime] = Query(None, description="Filter usage up to this date"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    recipient_location: Optional[str] = Query(None, description="Filter by recipient location"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_access_reports"))
):
    """
    Get blood usage records with filtering
    
    Requires: can_access_reports permission
    """
    service = BloodBankService(db)
    usage_records = service.get_usage_records(
        blood_group=blood_group,
        usage_date_from=usage_date_from,
        usage_date_to=usage_date_to,
        patient_id=patient_id,
        recipient_location=recipient_location,
        limit=limit,
        offset=offset
    )
    return usage_records

@router.get("/usage/{usage_id}", response_model=BloodUsageResponse)
def get_usage_record(
    usage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_access_reports"))
):
    """
    Get specific usage record by ID
    
    Requires: can_access_reports permission
    """
    from app.models.blood_usage import BloodUsage
    
    usage = db.query(BloodUsage).filter(BloodUsage.usage_id == usage_id).first()
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usage record {usage_id} not found"
        )
    return usage

@router.put("/usage/{usage_id}", response_model=BloodUsageResponse)
def update_usage_record(
    usage_id: int,
    update_data: BloodUsageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_inventory"))
):
    """
    Update usage record (e.g., crossmatch results, transfusion outcome)
    
    Requires: can_manage_inventory permission
    """
    from app.models.blood_usage import BloodUsage
    
    usage = db.query(BloodUsage).filter(BloodUsage.usage_id == usage_id).first()
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usage record {usage_id} not found"
        )
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(usage, field, value)
    
    usage.updated_at = datetime.utcnow()
    db.commit()
    
    return usage

# ==================== INVENTORY ENDPOINTS ====================

@router.get("/inventory", response_model=List[BloodInventoryResponse])
def get_current_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_view_analytics"))
):
    """
    Get current inventory levels for all blood groups
    
    Requires: can_view_analytics permission
    """
    service = BloodBankService(db)
    inventory = service.get_current_inventory()
    return inventory

@router.get("/inventory/{blood_group}", response_model=BloodInventoryResponse)
def get_inventory_by_blood_group(
    blood_group: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_view_analytics"))
):
    """
    Get inventory for specific blood group
    
    Requires: can_view_analytics permission
    """
    service = BloodBankService(db)
    inventory = service.get_inventory_by_blood_group(blood_group)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory for blood group {blood_group} not found"
        )
    return inventory

@router.put("/inventory/{blood_group}", response_model=BloodInventoryResponse)
def update_inventory_settings(
    blood_group: str,
    update_data: BloodInventoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_inventory"))
):
    """
    Update inventory thresholds and settings
    
    Requires: can_manage_inventory permission
    """
    try:
        service = BloodBankService(db)
        inventory = service.update_inventory_settings(blood_group, update_data)
        return inventory
    except Exception as e:
        logger.error(f"Error updating inventory settings for {blood_group}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update inventory settings: {str(e)}"
        )

# ==================== ALERTS AND MONITORING ====================

@router.get("/alerts/low-stock")
def get_low_stock_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_view_analytics"))
):
    """
    Get blood groups with low stock levels
    
    Requires: can_view_analytics permission
    """
    service = BloodBankService(db)
    alerts = service.get_low_stock_alerts()
    return {
        "timestamp": datetime.utcnow(),
        "total_alerts": len(alerts),
        "alerts": alerts
    }

@router.get("/alerts/expiry")
def get_expiry_alerts(
    days_ahead: int = Query(7, ge=1, le=30, description="Days ahead to check for expiry"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_view_analytics"))
):
    """
    Get blood units expiring within specified days
    
    Requires: can_view_analytics permission
    """
    service = BloodBankService(db)
    alerts = service.get_expiry_alerts(days_ahead)
    return {
        "timestamp": datetime.utcnow(),
        "days_ahead": days_ahead,
        "total_expiring_units": len(alerts),
        "total_expiring_volume_ml": sum(alert["volume_ml"] for alert in alerts),
        "expiring_units": alerts
    }

# ==================== ANALYTICS AND REPORTING ====================

@router.get("/analytics/dashboard")
def get_inventory_analytics(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to include in analytics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_view_analytics"))
):
    """
    Get comprehensive inventory analytics for dashboard
    
    Requires: can_view_analytics permission
    """
    service = BloodBankService(db)
    analytics = service.get_inventory_analytics(days_back)
    
    # Add summary metrics
    current_inventory = analytics["current_inventory"]
    total_current_volume = sum(inv["current_volume_ml"] for inv in current_inventory)
    total_available_volume = sum(inv["available_volume_ml"] for inv in current_inventory)
    
    # Count stock status categories
    stock_status_counts = {}
    for inv in current_inventory:
        status = inv["stock_status"]
        stock_status_counts[status] = stock_status_counts.get(status, 0) + 1
    
    analytics["summary"] = {
        "timestamp": datetime.utcnow(),
        "total_current_volume_ml": total_current_volume,
        "total_available_volume_ml": total_available_volume,
        "blood_groups_tracked": len(current_inventory),
        "stock_status_distribution": stock_status_counts,
        "period_collections": {
            "total_volume_ml": sum(col["total_volume_ml"] for col in analytics["collections"]),
            "total_units": sum(col["total_units"] for col in analytics["collections"])
        },
        "period_usage": {
            "total_volume_ml": sum(usage["total_volume_ml"] for usage in analytics["usage"]),
            "total_units": sum(usage["total_units"] for usage in analytics["usage"])
        }
    }
    
    return analytics

# ==================== DHIS2 INTEGRATION ====================

@router.post("/sync/dhis2", response_model=DHIS2SyncResponse)
def sync_with_dhis2(
    sync_request: DHIS2SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_users"))
):
    """
    Synchronize data with DHIS2
    
    Requires: can_manage_users permission (admin only)
    """
    # TODO: Implement DHIS2 synchronization
    # This is a placeholder for DHIS2 integration
    
    return DHIS2SyncResponse(
        total_records=len(sync_request.entity_ids),
        successful_syncs=0,
        failed_syncs=len(sync_request.entity_ids),
        sync_timestamp=datetime.utcnow(),
        failed_record_ids=sync_request.entity_ids,
        error_messages=["DHIS2 integration not yet implemented"]
    )

# ==================== SYSTEM STATUS ====================

@router.get("/system/status")
def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get blood bank system status
    
    Requires: Any authenticated user
    """
    try:
        # Get basic statistics
        from app.models.blood_donation import BloodDonation
        from app.models.blood_usage import BloodUsage
        from app.models.blood_inventory import BloodInventory
        
        total_donations = db.query(BloodDonation).count()
        total_usage_records = db.query(BloodUsage).count()
        blood_groups_tracked = db.query(BloodInventory).count()
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(hours=24)
        recent_donations = db.query(BloodDonation).filter(
            BloodDonation.created_at >= yesterday
        ).count()
        recent_usage = db.query(BloodUsage).filter(
            BloodUsage.created_at >= yesterday
        ).count()
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow(),
            "database_connected": True,
            "statistics": {
                "total_donations": total_donations,
                "total_usage_records": total_usage_records,
                "blood_groups_tracked": blood_groups_tracked,
                "recent_donations_24h": recent_donations,
                "recent_usage_24h": recent_usage
            },
            "user_permissions": {
                "can_manage_inventory": current_user.can_manage_inventory,
                "can_view_forecasts": current_user.can_view_forecasts,
                "can_manage_donors": current_user.can_manage_donors,
                "can_access_reports": current_user.can_access_reports,
                "can_manage_users": current_user.can_manage_users,
                "can_view_analytics": current_user.can_view_analytics
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return {
            "status": "error",
            "timestamp": datetime.utcnow(),
            "database_connected": False,
            "error": str(e)
        }
