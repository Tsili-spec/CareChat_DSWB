# 🩸 Blood Bank Database Schema - Updated Structure

## 📊 Database Overview
- **Database Type**: PostgreSQL
- **Tables**: 4 main tables
- **Status**: ✅ **Fully Updated** with all new features

---

## 🏗️ Updated Table Structures

### 1. **USERS Table** ✅ (No changes)
```sql
CREATE TABLE users (
    id                      SERIAL PRIMARY KEY,
    username                VARCHAR(50) NOT NULL UNIQUE,
    email                   VARCHAR(100) NOT NULL UNIQUE,
    full_name               VARCHAR(200) NOT NULL,
    hashed_password         VARCHAR(100) NOT NULL,
    role                    VARCHAR(50),
    department              VARCHAR(100),
    is_active               BOOLEAN,
    is_verified             BOOLEAN,
    last_login              TIMESTAMP,
    -- Permission flags
    can_manage_inventory    BOOLEAN,
    can_view_forecasts      BOOLEAN,
    can_manage_donors       BOOLEAN,
    can_access_reports      BOOLEAN,
    can_manage_users        BOOLEAN,
    can_view_analytics      BOOLEAN,
    -- Additional fields
    phone                   VARCHAR(20),
    address                 TEXT,
    employee_id             VARCHAR(50) UNIQUE,
    position                VARCHAR(100),
    license_number          VARCHAR(100),
    reset_token             VARCHAR(100),
    reset_token_expires     TIMESTAMP,
    failed_login_attempts   INTEGER,
    locked_until            TIMESTAMP,
    created_at              TIMESTAMP DEFAULT now(),
    updated_at              TIMESTAMP DEFAULT now(),
    created_by              INTEGER
);
```

### 2. **BLOOD_COLLECTIONS Table** ✅ (Updated)
```sql
CREATE TABLE blood_collections (
    donation_record_id      UUID PRIMARY KEY,
    donor_id                VARCHAR(50) NOT NULL,
    donor_name              VARCHAR(200) NOT NULL,
    donor_age               INTEGER NOT NULL,
    donor_gender            VARCHAR(1) NOT NULL,
    donor_occupation        VARCHAR(100),
    blood_type              VARCHAR(10) NOT NULL,
    collection_site         VARCHAR(200) NOT NULL,
    donation_date           DATE NOT NULL,           -- ✅ Changed from TIMESTAMP
    expiry_date             DATE NOT NULL,           -- ✅ Changed from TIMESTAMP
    collection_volume_ml    DOUBLE PRECISION NOT NULL,
    hemoglobin_g_dl         DOUBLE PRECISION NOT NULL,
    created_by              INTEGER REFERENCES users(id),
    created_at              TIMESTAMP DEFAULT now(),  -- Audit field
    updated_at              TIMESTAMP DEFAULT now()   -- Audit field
);

-- Indexes
CREATE INDEX ix_blood_collections_blood_type ON blood_collections(blood_type);
CREATE INDEX ix_blood_collections_donation_date ON blood_collections(donation_date);
CREATE INDEX ix_blood_collections_donor_id ON blood_collections(donor_id);
```

### 3. **BLOOD_USAGE Table** ✅ (Updated)
```sql
CREATE TABLE blood_usage (
    usage_id                UUID PRIMARY KEY,
    purpose                 VARCHAR(50) NOT NULL,
    department              VARCHAR(100) NOT NULL,
    blood_group             VARCHAR(10) NOT NULL,
    volume_given_out        DOUBLE PRECISION NOT NULL,
    usage_date              DATE NOT NULL DEFAULT CURRENT_DATE, -- ✅ Renamed from 'time', changed to DATE
    individual_name         VARCHAR(200) NOT NULL,
    patient_location        VARCHAR(200) NOT NULL,
    processed_by            INTEGER REFERENCES users(id),
    created_at              TIMESTAMP DEFAULT now(),  -- Audit field
    updated_at              TIMESTAMP DEFAULT now()   -- Audit field
);

-- Indexes
CREATE INDEX ix_blood_usage_blood_group ON blood_usage(blood_group);
CREATE INDEX ix_blood_usage_usage_date ON blood_usage(usage_date);
```

### 4. **BLOOD_STOCK Table** ✅ (Completely Updated)
```sql
CREATE TABLE blood_stock (
    stock_id                UUID PRIMARY KEY,
    blood_group             VARCHAR(10) NOT NULL,
    -- ✅ NEW STOCK TRACKING FIELDS
    total_available         DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    total_near_expiry       DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    total_expired           DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    -- ✅ UPDATED DATE FIELD
    stock_date              DATE NOT NULL DEFAULT CURRENT_DATE,
    -- Reference fields
    donation_record_id      UUID REFERENCES blood_collections(donation_record_id),
    usage_record_id         UUID REFERENCES blood_usage(usage_id),
    -- Audit fields
    created_at              TIMESTAMP DEFAULT now(),
    updated_at              TIMESTAMP DEFAULT now()  -- ✅ Added
);

-- Performance indexes
CREATE INDEX idx_blood_stock_blood_group_date ON blood_stock(blood_group, stock_date);
CREATE INDEX idx_blood_stock_donation_ref ON blood_stock(donation_record_id);
CREATE INDEX idx_blood_stock_usage_ref ON blood_stock(usage_record_id);
```

---

## 🎯 Key Improvements

### ✅ **Enhanced Stock Tracking**
- **`total_available`**: Current usable blood volume
- **`total_near_expiry`**: Volume expiring within 7 days
- **`total_expired`**: Volume that has expired
- **Automatic updates**: Stock is updated when donations/usage are recorded

### ✅ **Date-Only Fields**
- **Collection dates**: Only date, no time component
- **Usage dates**: Only date, no time component  
- **Stock dates**: Only date, no time component
- **Audit fields**: Still use TIMESTAMP for precise tracking

### ✅ **Improved Relationships**
- Proper foreign key constraints
- Optimized indexes for performance
- Clear referential integrity

---

## 🔧 **Functional Features**

### **Automatic Stock Management**
When a blood donation is recorded:
1. Updates `total_available` with new volume
2. Calculates `total_near_expiry` based on expiry dates
3. Calculates `total_expired` for expired units
4. Creates stock record with proper references

### **Real-time Inventory**
- API endpoints return enhanced stock data
- Expiry tracking for better blood management
- Low stock and expiry alerts
- Historical tracking capability

### **Enhanced Authentication**
- Login returns both access and refresh tokens
- Longer-lived refresh tokens (30 days)
- Improved security with token type identification

---

## 📋 **API Response Examples**

### **Updated Inventory Response**
```json
{
  "blood_group": "A+",
  "total_available": 2500.0,
  "total_near_expiry": 450.0,
  "total_expired": 0.0,
  "available_units": 5,
  "last_updated": "2025-07-31T18:14:24Z"
}
```

### **Updated Authentication Response**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "permissions": { ... }
}
```

---

## ✅ **Migration Status**

| Component | Status | Notes |
|-----------|--------|-------|
| Database Schema | ✅ Complete | All tables recreated |
| Stock Tracking | ✅ Complete | New fields added |
| Date Fields | ✅ Complete | TIMESTAMP → DATE |
| Authentication | ✅ Complete | Dual tokens |
| API Endpoints | ✅ Complete | Updated responses |
| Environment Config | ✅ Complete | .env file setup |

The database is now fully updated and ready for production use with all the enhanced features!
