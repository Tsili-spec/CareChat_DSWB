from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import pandas as pd
import io

from app.db.database import get_db
from app.core.auth import get_current_user, require_permission
from app.models.user import User
from app.schemas.blood_bank import (
    BloodCollectionCreate, BloodCollectionUpdate, BloodCollectionResponse,
    BloodUsageCreate, BloodUsageUpdate, BloodUsageResponse,
    BloodInventorySummary, InventoryAlert, DHIS2SyncRequest, DHIS2SyncResponse
)
from app.services.blood_bank_service import BloodBankService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/blood-bank")

# ==================== COLLECTION ENDPOINTS ====================

@router.post("/collections", response_model=BloodCollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    collection_data: BloodCollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_donors"))
):
    """
    Create a new blood collection record
    
    Requires: can_manage_donors permission
    """
    try:
        service = BloodBankService(db)
        collection = service.create_collection(collection_data, current_user.user_id)
        return collection
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create collection: {str(e)}"
        )

@router.get("/collections", response_model=List[BloodCollectionResponse])
def get_collections(
    blood_type: Optional[str] = Query(None, description="Filter by blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)"),
    collection_date_from: Optional[datetime] = Query(None, description="Filter collections from this date"),
    collection_date_to: Optional[datetime] = Query(None, description="Filter collections up to this date"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_view_analytics"))
):
    """
    Get blood collection records with filtering
    
    Requires: can_view_analytics permission
    """
    service = BloodBankService(db)
    collections = service.get_collections(
        blood_type=blood_type,
        collection_date_from=collection_date_from,
        collection_date_to=collection_date_to,
        limit=limit,
        offset=offset
    )
    return collections


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
        usage = service.create_usage(usage_data, current_user.user_id)
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
    patient_location: Optional[str] = Query(None, description="Filter by patient location"),
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
        patient_location=patient_location,
        limit=limit,
        offset=offset
    )
    return usage_records

# ==================== INVENTORY ENDPOINTS ====================

@router.get("/inventory", response_model=List[BloodInventorySummary])
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

@router.get("/inventory/{blood_group}", response_model=BloodInventorySummary)
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
        # Get basic statistics using new models
        from app.models.blood_collection import BloodCollection
        from app.models.blood_usage import BloodUsage
        from app.models.blood_stock import BloodStock
        
        total_collections = db.query(BloodCollection).count()
        total_usage_records = db.query(BloodUsage).count()
        total_stock_records = db.query(BloodStock).count()
        
        # Get recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(hours=24)
        recent_collections = db.query(BloodCollection).filter(
            BloodCollection.created_at >= yesterday
        ).count()
        recent_usage = db.query(BloodUsage).filter(
            BloodUsage.created_at >= yesterday
        ).count()
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow(),
            "database_connected": True,
            "statistics": {
                "total_collections": total_collections,
                "total_usage_records": total_usage_records,
                "total_stock_records": total_stock_records,
                "recent_collections_24h": recent_collections,
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

# ==================== CSV UPLOAD ENDPOINTS ====================

@router.post("/collections/upload-csv", status_code=status.HTTP_201_CREATED)
async def upload_collections_csv(
    file: UploadFile = File(..., description="CSV file with blood collection data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_donors"))
):
    """
    Upload blood collection data from CSV file
    
    Expected CSV columns:
    - donor_age (required): Age of donor (18-70)
    - donor_gender (required): M or F
    - donor_occupation (optional): Donor's occupation
    - blood_type (required): A+, A-, B+, B-, AB+, AB-, O+, O-
    - collection_site (required): Collection site name
    - donation_date (required): Date in YYYY-MM-DD format
    - expiry_date (required): Date in YYYY-MM-DD format
    - collection_volume_ml (required): Volume in ml (1-500)
    - hemoglobin_g_dl (required): Hemoglobin level (1-20)
    
    Requires: can_manage_donors permission
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate required columns
        required_columns = [
            'donor_age', 'donor_gender', 'blood_type', 'collection_site',
            'donation_date', 'expiry_date', 'collection_volume_ml', 'hemoglobin_g_dl'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Clean and validate data
        service = BloodBankService(db)
        successful_uploads = 0
        failed_uploads = []
        
        logger.info(f"Processing {len(df)} collection records from CSV")
        
        for index, row in df.iterrows():
            try:
                # Skip rows with missing critical data
                if pd.isna(row['donor_age']) or pd.isna(row['donor_gender']) or pd.isna(row['blood_type']):
                    failed_uploads.append(f"Row {index + 1}: Missing critical data")
                    continue
                
                # Create collection data
                collection_data = BloodCollectionCreate(
                    donor_age=int(row['donor_age']),
                    donor_gender=str(row['donor_gender']).upper(),
                    donor_occupation=str(row.get('donor_occupation', 'Unknown')),
                    blood_type=str(row['blood_type']),
                    collection_site=str(row['collection_site']),
                    donation_date=pd.to_datetime(row['donation_date']).date(),
                    expiry_date=pd.to_datetime(row['expiry_date']).date(),
                    collection_volume_ml=float(row['collection_volume_ml']),
                    hemoglobin_g_dl=float(row['hemoglobin_g_dl'])
                )
                
                # Create collection record
                collection = service.create_collection(collection_data, current_user.user_id)
                successful_uploads += 1
                
            except Exception as e:
                failed_uploads.append(f"Row {index + 1}: {str(e)}")
        
        return {
            "message": f"CSV upload completed",
            "total_records": len(df),
            "successful_uploads": successful_uploads,
            "failed_uploads": len(failed_uploads),
            "failures": failed_uploads[:10],  # Show first 10 failures
            "has_more_failures": len(failed_uploads) > 10
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty"
        )
    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing CSV file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error uploading collections CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV file: {str(e)}"
        )

@router.post("/usage/upload-csv", status_code=status.HTTP_201_CREATED)
async def upload_usage_csv(
    file: UploadFile = File(..., description="CSV file with blood usage data"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("can_manage_inventory"))
):
    """
    Upload blood usage data from CSV file
    
    Expected CSV columns:
    - purpose (required): Purpose of blood usage (string)
    - department (required): Department name
    - blood_group (required): A+, A-, B+, B-, AB+, AB-, O+, O-
    - volume_given_out (required): Volume in ml (1-500)
    - usage_date (required): Date in YYYY-MM-DD format
    - individual_name (optional): Patient name
    - patient_location (required): Hospital/location name
    
    Requires: can_manage_inventory permission
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        # Read CSV content
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate required columns
        required_columns = [
            'purpose', 'department', 'blood_group', 'volume_given_out',
            'usage_date', 'patient_location'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Clean and validate data
        service = BloodBankService(db)
        successful_uploads = 0
        failed_uploads = []
        
        logger.info(f"Processing {len(df)} usage records from CSV")
        
        for index, row in df.iterrows():
            try:
                # Skip rows with missing critical data
                if (pd.isna(row['purpose']) or pd.isna(row['department']) or 
                    pd.isna(row['blood_group']) or pd.isna(row['volume_given_out'])):
                    failed_uploads.append(f"Row {index + 1}: Missing critical data")
                    continue
                
                # Create usage data
                usage_data = BloodUsageCreate(
                    purpose=str(row['purpose']),
                    department=str(row['department']),
                    blood_group=str(row['blood_group']),
                    volume_given_out=float(row['volume_given_out']),
                    usage_date=pd.to_datetime(row['usage_date']).date(),
                    individual_name=str(row.get('individual_name', 'Unknown Patient')),
                    patient_location=str(row['patient_location'])
                )
                
                # Create usage record
                usage = service.create_usage(usage_data, current_user.user_id)
                successful_uploads += 1
                
            except Exception as e:
                failed_uploads.append(f"Row {index + 1}: {str(e)}")
        
        return {
            "message": f"CSV upload completed",
            "total_records": len(df),
            "successful_uploads": successful_uploads,
            "failed_uploads": len(failed_uploads),
            "failures": failed_uploads[:10],  # Show first 10 failures
            "has_more_failures": len(failed_uploads) > 10
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty"
        )
    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parsing CSV file: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error uploading usage CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV file: {str(e)}"
        )