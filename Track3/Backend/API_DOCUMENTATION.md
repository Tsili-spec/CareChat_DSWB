# 🩸 Blood Bank Management System - Complete API Documentation

**Base URL:** `https://blood-management-system-xplx.onrender.com`

## 📋 Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [Blood Collection Endpoints](#blood-collection-endpoints)
3. [Blood Usage Endpoints](#blood-usage-endpoints)
4. [Inventory Management Endpoints](#inventory-management-endpoints)
5. [Analytics Endpoints](#analytics-endpoints)
6. [Alert System Endpoints](#alert-system-endpoints)
7. [System Status Endpoints](#system-status-endpoints)
8. [CSV Upload Endpoints](#csv-upload-endpoints)
9. [DHIS2 Integration Endpoints](#dhis2-integration-endpoints)
10. [Default Users & Authentication](#default-users--authentication)
11. [Error Responses](#error-responses)

---

## 🔐 Authentication Endpoints

### 1. Register User
**POST** `https://blood-management-system-xplx.onrender.com/api/v1/auth/register`

Creates a new user account with automatic permission assignment based on role.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john.doe@hospital.com",
  "full_name": "John Doe",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "role": "staff",
  "phone": "+1234567890"
}
```

**Sample Response (201 Created):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john.doe@hospital.com",
  "full_name": "John Doe",
  "role": "staff",
  "phone": "+1234567890",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-08-01T09:30:00.000Z",
  "can_manage_inventory": false,
  "can_view_forecasts": true,
  "can_manage_donors": true,
  "can_access_reports": true,
  "can_manage_users": false,
  "can_view_analytics": true
}
```

**Available Roles:**
- `admin` - Full access to all features
- `manager` - Manage inventory, donors, reports, analytics
- `staff` - Manage donors, view reports and analytics
- `viewer` - View reports and analytics only

---

### 2. Login User
**POST** `https://blood-management-system-xplx.onrender.com/api/v1/auth/login`

Authenticates user and returns JWT access token.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Sample Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwidXNlcl9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCIsImV4cCI6MTczNTc0ODQwMH0.abc123def456ghi789",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huZG9lIiwidXNlcl9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCIsImV4cCI6MTczNTc0ODQwMH0.xyz789abc123def456",
  "token_type": "bearer",
  "expires_in": 604800,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "role": "staff",
  "permissions": {
    "can_manage_inventory": false,
    "can_view_forecasts": true,
    "can_manage_donors": true,
    "can_access_reports": true,
    "can_manage_users": false,
    "can_view_analytics": true
  }
}
```

---

### 3. Change Password
**POST** `https://blood-management-system-xplx.onrender.com/api/v1/auth/change-password`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "current_password": "SecurePass123!",
  "new_password": "NewSecurePass456!",
  "confirm_new_password": "NewSecurePass456!"
}
```

**Sample Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

### 4. List All Users (Admin Only)
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/auth/users`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 100)

**Sample Response (200 OK):**
```json
[
  {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "johndoe",
    "email": "john.doe@hospital.com",
    "full_name": "John Doe",
    "role": "staff",
    "is_active": true,
    "created_at": "2025-08-01T09:30:00.000Z",
    "last_login": "2025-08-01T10:15:00.000Z"
  }
]
```

---

### 5. Delete User (Admin Only)
**DELETE** `https://blood-management-system-xplx.onrender.com/api/v1/auth/users/{user_id}`

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Sample Response (200 OK):**
```json
{
  "message": "User johndoe deleted successfully"
}
```

---

## 🩸 Blood Collection Endpoints

### 6. Create Blood Collection Record
**POST** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/collections`

**Permission Required:** `can_manage_donors`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "donor_age": 25,
  "donor_gender": "M",
  "donor_occupation": "Teacher",
  "blood_type": "A+",
  "collection_site": "City Hospital Blood Bank",
  "donation_date": "2025-08-01",
  "expiry_date": "2025-09-15",
  "collection_volume_ml": 450.0,
  "hemoglobin_g_dl": 14.5
}
```

**Sample Response (201 Created):**
```json
{
  "donation_record_id": "rec_550e8400-e29b-41d4-a716-446655440000",
  "donor_age": 25,
  "donor_gender": "M",
  "donor_occupation": "Teacher",
  "blood_type": "A+",
  "collection_site": "City Hospital Blood Bank",
  "donation_date": "2025-08-01",
  "expiry_date": "2025-09-15",
  "collection_volume_ml": 450.0,
  "hemoglobin_g_dl": 14.5,
  "created_at": "2025-08-01T09:30:00.000Z",
  "updated_at": "2025-08-01T09:30:00.000Z"
}
```

---

### 7. Get Blood Collection Records
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/collections`

**Permission Required:** `can_view_analytics`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Query Parameters:**
- `blood_type` (optional): Filter by blood type (A+, A-, B+, B-, AB+, AB-, O+, O-)
- `collection_date_from` (optional): Filter from this date (YYYY-MM-DD)
- `collection_date_to` (optional): Filter up to this date (YYYY-MM-DD)
- `limit` (optional): Maximum records to return (1-1000, default: 100)
- `offset` (optional): Number of records to skip (default: 0)

**Sample Response (200 OK):**
```json
[
  {
    "donation_record_id": "rec_550e8400-e29b-41d4-a716-446655440000",
    "donor_age": 25,
    "donor_gender": "M",
    "donor_occupation": "Teacher",
    "blood_type": "A+",
    "collection_site": "City Hospital Blood Bank",
    "donation_date": "2025-08-01",
    "expiry_date": "2025-09-15",
    "collection_volume_ml": 450.0,
    "hemoglobin_g_dl": 14.5,
    "created_at": "2025-08-01T09:30:00.000Z",
    "updated_at": "2025-08-01T09:30:00.000Z"
  }
]
```

---

## 🏥 Blood Usage Endpoints

### 8. Record Blood Usage
**POST** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/usage`

**Permission Required:** `can_manage_inventory`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "purpose": "Emergency Surgery",
  "department": "Emergency Department",
  "blood_group": "A+",
  "volume_given_out": 450.0,
  "usage_date": "2025-08-01",
  "individual_name": "John Patient",
  "patient_location": "City General Hospital"
}
```

**Sample Response (201 Created):**
```json
{
  "usage_record_id": "usage_550e8400-e29b-41d4-a716-446655440000",
  "purpose": "Emergency Surgery",
  "department": "Emergency Department",
  "blood_group": "A+",
  "volume_given_out": 450.0,
  "usage_date": "2025-08-01",
  "individual_name": "John Patient",
  "patient_location": "City General Hospital",
  "created_at": "2025-08-01T09:30:00.000Z",
  "updated_at": "2025-08-01T09:30:00.000Z"
}
```

---

### 9. Get Blood Usage Records
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/usage`

**Permission Required:** `can_access_reports`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Query Parameters:**
- `blood_group` (optional): Filter by blood group
- `usage_date_from` (optional): Filter from this date (YYYY-MM-DD)
- `usage_date_to` (optional): Filter up to this date (YYYY-MM-DD)
- `patient_location` (optional): Filter by patient location
- `limit` (optional): Maximum records to return (1-1000, default: 100)
- `offset` (optional): Number of records to skip (default: 0)

**Sample Response (200 OK):**
```json
[
  {
    "usage_record_id": "usage_550e8400-e29b-41d4-a716-446655440000",
    "purpose": "Emergency Surgery",
    "department": "Emergency Department",
    "blood_group": "A+",
    "volume_given_out": 450.0,
    "usage_date": "2025-08-01",
    "individual_name": "John Patient",
    "patient_location": "City General Hospital",
    "created_at": "2025-08-01T09:30:00.000Z",
    "updated_at": "2025-08-01T09:30:00.000Z"
  }
]
```

---

## 📊 Inventory Management Endpoints

### 10. Get Current Inventory
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/inventory`

**Permission Required:** `can_view_analytics`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Sample Response (200 OK):**
```json
[
  {
    "blood_group": "A+",
    "total_available": 2500.0,
    "total_reserved": 450.0,
    "total_expired": 0.0,
    "near_expiry_count": 2,
    "last_updated": "2025-08-01T09:30:00.000Z",
    "status": "adequate",
    "minimum_threshold": 1000.0
  },
  {
    "blood_group": "O-",
    "total_available": 800.0,
    "total_reserved": 200.0,
    "total_expired": 50.0,
    "near_expiry_count": 1,
    "last_updated": "2025-08-01T09:30:00.000Z",
    "status": "low",
    "minimum_threshold": 1200.0
  }
]
```

---

### 11. Get Inventory by Blood Group
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/inventory/{blood_group}`

**Permission Required:** `can_view_analytics`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Path Parameters:**
- `blood_group`: Blood group (A+, A-, B+, B-, AB+, AB-, O+, O-)

**Sample Response (200 OK):**
```json
{
  "blood_group": "A+",
  "total_available": 2500.0,
  "total_reserved": 450.0,
  "total_expired": 0.0,
  "near_expiry_count": 2,
  "last_updated": "2025-08-01T09:30:00.000Z",
  "status": "adequate",
  "minimum_threshold": 1000.0
}
```

---

## 🔔 Alert System Endpoints

### 12. Get Low Stock Alerts
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/alerts/low-stock`

**Permission Required:** `can_view_analytics`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Sample Response (200 OK):**
```json
{
  "timestamp": "2025-08-01T09:30:00.000Z",
  "total_alerts": 2,
  "alerts": [
    {
      "blood_group": "O-",
      "current_stock": 800.0,
      "minimum_threshold": 1200.0,
      "shortage": 400.0,
      "severity": "critical",
      "message": "Critical shortage: O- blood group is 400ml below minimum threshold"
    },
    {
      "blood_group": "AB-",
      "current_stock": 150.0,
      "minimum_threshold": 300.0,
      "shortage": 150.0,
      "severity": "low",
      "message": "Low stock: AB- blood group is 150ml below minimum threshold"
    }
  ]
}
```

---

### 13. Get Expiry Alerts
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/alerts/expiry`

**Permission Required:** `can_view_analytics`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Query Parameters:**
- `days_ahead` (optional): Days ahead to check for expiry (1-30, default: 7)

**Sample Response (200 OK):**
```json
{
  "timestamp": "2025-08-01T09:30:00.000Z",
  "days_ahead": 7,
  "total_expiring": 3,
  "total_volume": 1350.0,
  "expiring_units": [
    {
      "donation_record_id": "rec_123",
      "blood_group": "A+",
      "volume_ml": 450.0,
      "expiry_date": "2025-08-05",
      "days_until_expiry": 4,
      "collection_site": "City Hospital"
    },
    {
      "donation_record_id": "rec_124",
      "blood_group": "O+",
      "volume_ml": 450.0,
      "expiry_date": "2025-08-07",
      "days_until_expiry": 6,
      "collection_site": "General Hospital"
    }
  ]
}
```

---

## 📈 Analytics Endpoints

### 14. Get Daily Volume Trends
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/analytics/daily-volume-trends`

**Permission Required:** `can_view_analytics`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Query Parameters:**
- `days` (optional): Number of days to include (1-90, default: 30)
- `blood_types` (optional): Array of blood types to include

**Sample Response (200 OK):**
```json
{
  "period": {
    "start_date": "2025-07-02",
    "end_date": "2025-08-01",
    "days": 30
  },
  "blood_types": ["A+", "O+", "B+"],
  "trends": {
    "A+": {
      "dates": ["2025-07-02", "2025-07-03", "2025-07-04"],
      "donated_volume": [450.0, 900.0, 450.0],
      "used_volume": [200.0, 450.0, 300.0],
      "stock_volume": [2500.0, 2850.0, 3000.0]
    },
    "O+": {
      "dates": ["2025-07-02", "2025-07-03", "2025-07-04"],
      "donated_volume": [900.0, 450.0, 1350.0],
      "used_volume": [450.0, 200.0, 600.0],
      "stock_volume": [3200.0, 3450.0, 4200.0]
    }
  }
}
```

---

### 15. Get Volume by Blood Type
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/analytics/volume-by-blood-type`

**Permission Required:** `can_view_analytics`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Query Parameters:**
- `days` (optional): Number of days to analyze (1-365, default: 30)

**Sample Response (200 OK):**
```json
{
  "period": {
    "start_date": "2025-07-02",
    "end_date": "2025-08-01",
    "days": 30
  },
  "volume_comparison": [
    {
      "blood_type": "A+",
      "total_donated": 4500.0,
      "total_used": 3200.0,
      "net_balance": 1300.0,
      "donation_percentage": 28.5,
      "usage_percentage": 31.2
    },
    {
      "blood_type": "O+",
      "total_donated": 5400.0,
      "total_used": 4100.0,
      "net_balance": 1300.0,
      "donation_percentage": 34.2,
      "usage_percentage": 40.0
    }
  ],
  "summary": {
    "total_donated": 15750.0,
    "total_used": 10250.0,
    "overall_net_balance": 5500.0
  }
}
```

---

### 16. Get Daily Total Volume
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/analytics/daily-total-volume`

**Permission Required:** `can_view_analytics`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Query Parameters:**
- `days` (optional): Number of days to analyze (1-90, default: 30)

**Sample Response (200 OK):**
```json
{
  "period": {
    "start_date": "2025-07-02",
    "end_date": "2025-08-01",
    "days": 30
  },
  "daily_totals": [
    {
      "date": "2025-07-02",
      "total_donated": 1350.0,
      "total_used": 650.0,
      "net_change": 700.0
    },
    {
      "date": "2025-07-03",
      "total_donated": 1800.0,
      "total_used": 950.0,
      "net_change": 850.0
    }
  ],
  "statistics": {
    "avg_daily_donation": 1575.0,
    "avg_daily_usage": 800.0,
    "avg_net_change": 775.0,
    "total_period_donation": 47250.0,
    "total_period_usage": 24000.0
  }
}
```

---

### 17. Get Inventory Optimization
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/analytics/inventory-optimization`

**Permission Required:** `can_view_forecasts`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Query Parameters:**
- `forecast_days` (optional): Days to forecast (1-30, default: 7)
- `lead_time_days` (optional): Lead time for procurement (1-14, default: 3)
- `max_order_limit` (optional): Maximum order quantity (100-1000, default: 500)

**Sample Response (200 OK):**
```json
{
  "forecast_period": {
    "start_date": "2025-08-02",
    "end_date": "2025-08-08",
    "days": 7
  },
  "optimization_results": [
    {
      "blood_group": "A+",
      "current_stock": 2500.0,
      "predicted_usage": 1200.0,
      "predicted_donations": 800.0,
      "projected_stock": 2100.0,
      "recommended_order": 0,
      "status": "adequate",
      "notes": "Stock levels sufficient for forecast period"
    },
    {
      "blood_group": "O-",
      "current_stock": 800.0,
      "predicted_usage": 900.0,
      "predicted_donations": 300.0,
      "projected_stock": 200.0,
      "recommended_order": 500,
      "status": "order_required",
      "notes": "Critical stock level predicted, immediate order recommended"
    }
  ],
  "summary": {
    "total_current_stock": 12500.0,
    "total_predicted_usage": 5400.0,
    "total_predicted_donations": 3200.0,
    "total_recommended_orders": 1000.0
  }
}
```

---

## 🖥️ System Status Endpoints

### 18. Get System Status
**GET** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/system/status`

**Headers:**
```
Authorization: Bearer <your_access_token>
```

**Sample Response (200 OK):**
```json
{
  "status": "operational",
  "timestamp": "2025-08-01T09:30:00.000Z",
  "database_connected": true,
  "statistics": {
    "total_collections": 1250,
    "total_usage_records": 850,
    "total_stock_records": 324,
    "recent_collections_24h": 15,
    "recent_usage_24h": 8
  },
  "user_permissions": {
    "can_manage_inventory": true,
    "can_view_forecasts": true,
    "can_manage_donors": true,
    "can_access_reports": true,
    "can_manage_users": false,
    "can_view_analytics": true
  }
}
```

---

### 19. Health Check
**GET** `https://blood-management-system-xplx.onrender.com/health`

**Sample Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0",
  "schema": "blood_collections, blood_usage, blood_stock, users"
}
```

---

### 20. Root Endpoint
**GET** `https://blood-management-system-xplx.onrender.com/`

**Sample Response (200 OK):**
```json
{
  "message": "Welcome to Blood Bank Management System API",
  "version": "1.0.0",
  "architecture": "3-Table Blood Bank System (Collections, Usage, Stock)",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

## 📁 CSV Upload Endpoints

### 21. Upload Blood Collections CSV
**POST** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/collections/upload-csv`

**Permission Required:** `can_manage_donors`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
Form Data:
file: collections.csv (CSV file)
```

**Required CSV Columns:**
- `donor_age`
- `donor_gender` 
- `donor_occupation`
- `blood_type`
- `collection_site`
- `donation_date`
- `expiry_date`
- `collection_volume_ml`
- `hemoglobin_g_dl`

**Sample Response (201 Created):**
```json
{
  "message": "Successfully uploaded blood collections data",
  "total_records": 150,
  "successful_imports": 148,
  "failed_imports": 2,
  "errors": [
    {
      "row": 5,
      "error": "Invalid blood type: XY+"
    },
    {
      "row": 12,
      "error": "Donor age must be between 18 and 70"
    }
  ]
}
```

---

### 22. Upload Blood Usage CSV
**POST** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/usage/upload-csv`

**Permission Required:** `can_manage_inventory`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
Form Data:
file: usage.csv (CSV file)
```

**Required CSV Columns:**
- `purpose`
- `department`
- `blood_group`
- `volume_given_out`
- `usage_date`
- `patient_location`

**Optional CSV Columns:**
- `individual_name`

**Sample Response (201 Created):**
```json
{
  "message": "Successfully uploaded blood usage data",
  "total_records": 85,
  "successful_imports": 83,
  "failed_imports": 2,
  "errors": [
    {
      "row": 8,
      "error": "Invalid date format for usage_date"
    },
    {
      "row": 23,
      "error": "Volume must be greater than 0"
    }
  ]
}
```

---

## 🌐 DHIS2 Integration Endpoints

### 23. Sync with DHIS2
**POST** `https://blood-management-system-xplx.onrender.com/api/v1/blood-bank/sync/dhis2`

**Permission Required:** `can_manage_users`

**Headers:**
```
Authorization: Bearer <your_access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "sync_collections": true,
  "sync_usage": true,
  "date_range": {
    "start_date": "2025-07-01",
    "end_date": "2025-08-01"
  },
  "dhis2_config": {
    "base_url": "https://play.dhis2.org/2.39.1.1",
    "username": "admin",
    "password": "district"
  }
}
```

**Sample Response (200 OK):**
```json
{
  "sync_status": "completed",
  "timestamp": "2025-08-01T09:30:00.000Z",
  "collections_synced": 125,
  "usage_synced": 89,
  "errors": [],
  "dhis2_response": {
    "status": "SUCCESS",
    "imported": 214,
    "updated": 0,
    "ignored": 0
  }
}
```

---

## 👤 Default Users & Authentication

The system comes with pre-configured users for testing:

### Administrator
- **Username:** `admin`
- **Password:** `Admin123!`
- **Role:** `admin`
- **Permissions:** All permissions enabled

### Manager
- **Username:** `manager1`
- **Password:** `Manager123!`
- **Role:** `manager`
- **Permissions:** All except user management

### Staff Member
- **Username:** `staff1`
- **Password:** `Staff123!`
- **Role:** `staff`
- **Permissions:** Donor management, reports, analytics

### Viewer
- **Username:** `viewer1`
- **Password:** `Viewer123!`
- **Role:** `viewer`
- **Permissions:** Reports and analytics only

---

## ❌ Error Responses

### Authentication Errors

**401 Unauthorized - Invalid Credentials:**
```json
{
  "detail": "Invalid username or password",
  "status_code": 401
}
```

**401 Unauthorized - Token Invalid:**
```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

**403 Forbidden - Insufficient Permissions:**
```json
{
  "detail": "Access denied. Required permission: can_manage_inventory",
  "status_code": 403
}
```

### Validation Errors

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "type": "value_error"
    },
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "status_code": 422
}
```

### Business Logic Errors

**400 Bad Request:**
```json
{
  "detail": "Username already registered",
  "status_code": 400
}
```

**404 Not Found:**
```json
{
  "detail": "User not found",
  "status_code": 404
}
```

### Server Errors

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error occurred",
  "status_code": 500
}
```

---

## 🔑 Authentication Flow

1. **Register or use default user credentials**
2. **Login to get access token**
3. **Include token in Authorization header for all protected endpoints:**
   ```
   Authorization: Bearer <your_access_token>
   ```
4. **Tokens expire after 7 days (604800 seconds)**

## 📊 Permission Matrix

| Permission | Admin | Manager | Staff | Viewer |
|------------|-------|---------|-------|--------|
| `can_manage_users` | ✅ | ❌ | ❌ | ❌ |
| `can_manage_inventory` | ✅ | ✅ | ❌ | ❌ |
| `can_manage_donors` | ✅ | ✅ | ✅ | ❌ |
| `can_access_reports` | ✅ | ✅ | ✅ | ✅ |
| `can_view_forecasts` | ✅ | ✅ | ✅ | ✅ |
| `can_view_analytics` | ✅ | ✅ | ✅ | ✅ |

---

**🩸 Blood Bank Management System API** - Comprehensive healthcare data management with advanced analytics and forecasting capabilities.

*Last updated: August 1, 2025*
