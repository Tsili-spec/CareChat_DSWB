# Blood Bank System - Migration Guide

This document describes the major updates implemented in the blood bank management system.

## Summary of Changes

### 1. Authentication Updates
- **Login endpoint now returns both access and refresh tokens**
- **Removed the `/refresh` endpoint** - refresh tokens are now provided at login
- Updated JWT token structure to include token type identification

### 2. Database Schema Updates

#### Stock Table Enhancements
The `blood_stock` table now includes:
- `total_available`: Total available blood volume (ml)
- `total_near_expiry`: Volume expiring within 7 days (ml)  
- `total_expired`: Volume that has expired (ml)
- `stock_date`: Date field (changed from datetime)

#### Date Field Updates
Time fields changed to date-only fields (except audit columns):
- `blood_collections.donation_date`: DateTime → Date
- `blood_collections.expiry_date`: DateTime → Date
- `blood_usage.usage_date`: DateTime → Date (renamed from `time`)
- `blood_stock.stock_date`: DateTime → Date (renamed from `time`)

*Note: Audit columns (`created_at`, `updated_at`) remain as DateTime for tracking purposes.*

### 3. Configuration Updates
- **Created new `.env` file** with database URL and secret key
- **Updated `config.py`** to load from environment variables:
  - `DATABASE_URL` - Direct PostgreSQL connection string
  - `SECRET_KEY` - JWT authentication secret

### 4. Stock Management Automation
- Stock levels are automatically updated when:
  - New blood donations are recorded
  - Blood usage is recorded
- Expiry categories are automatically calculated based on collection dates
- Real-time inventory tracking with expiry alerts

### 5. API Enhancements
- Updated inventory endpoints to return new stock fields
- Enhanced stock data includes available, near-expiry, and expired volumes
- Improved error handling and validation

## Environment Setup

### Required Environment Variables
Create a `.env` file in the project root with:

```env
# Database Configuration
DATABASE_URL=postgresql://blood_bank_system_5f0v_user:CKb66TEscgU1z4qwUszOVn4SXrTzUFLn@dpg-d257s4c9c44c73b9valg-a.oregon-postgres.render.com/blood_bank_system_5f0v

# Security Configuration
SECRET_KEY=your-super-secret-key-for-jwt-authentication-please-change-this-in-production-environment
```

### Database Migration

To migrate your existing database to the new schema:

```bash
# Run the migration script
python scripts/migrate_database.py
```

This will:
- Add new columns to existing tables
- Migrate existing data to new fields
- Create necessary indexes
- Preserve existing data for safety

## API Changes

### Authentication Endpoints

#### Login Response (Updated)
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user_id": 1,
  "username": "admin",
  "role": "admin",
  "permissions": {
    "can_manage_inventory": true,
    "can_view_forecasts": true,
    "can_manage_donors": true,
    "can_access_reports": true,
    "can_manage_users": true,
    "can_view_analytics": true
  }
}
```

#### Removed Endpoints
- `POST /api/v1/auth/refresh` - No longer needed

### Inventory Endpoints (Updated)

#### Get Inventory Response
```json
[
  {
    "blood_group": "A+",
    "total_available": 2500.0,
    "total_near_expiry": 450.0,
    "total_expired": 0.0,
    "available_units": 5,
    "last_updated": "2024-01-15T10:30:00Z"
  }
]
```

## Breaking Changes

### Client Applications
1. **Update login handling** to store both access and refresh tokens
2. **Remove refresh token logic** - use refresh token from login response
3. **Update inventory displays** to show new stock categories
4. **Update date handling** for collection and usage dates (no time component)

### Database Queries
1. **Update queries** using old column names:
   - `volume_in_stock` → `total_available`
   - `time` → `stock_date` (blood_stock)
   - `time` → `usage_date` (blood_usage)

## Testing

### Verify Migration
1. Check that all tables have new columns
2. Verify existing data is preserved
3. Test stock calculations with new donations/usage
4. Confirm API responses include new fields

### Test Authentication
1. Login and verify both tokens are returned
2. Verify refresh token has longer expiration
3. Test API access with new token structure

## Production Deployment

### Pre-deployment Checklist
- [ ] Update `.env` file with production values
- [ ] Change `SECRET_KEY` to production-safe value
- [ ] Run database migration script
- [ ] Update client applications
- [ ] Test all endpoints

### Security Notes
- Generate a strong `SECRET_KEY` for production
- Ensure `.env` file is not committed to version control
- Consider using environment-specific configuration files

## Support

For issues or questions regarding this migration:
1. Check the logs for detailed error messages
2. Verify environment variables are correctly set
3. Ensure database connectivity
4. Review the migration script output for any warnings
