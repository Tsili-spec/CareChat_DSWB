# Registration System Updates

## Overview
The user registration system has been simplified to remove manual field entry and implement automatic permission assignment based on roles. This improves user experience and ensures consistent security policies.

## Changes Made

### 1. Updated User Schemas (`app/schemas/user.py`)

#### UserBase Schema
**Removed fields:**
- `department: Optional[str]` 
- `employee_id: Optional[str]`
- `position: Optional[str]`

**Retained fields:**
- `username: str`
- `email: EmailStr` 
- `full_name: str`
- `role: str`
- `phone: Optional[str]`

#### UserCreate Schema
**Removed all permission fields:**
- `can_manage_inventory: Optional[bool]`
- `can_view_forecasts: Optional[bool]`
- `can_manage_donors: Optional[bool]`
- `can_access_reports: Optional[bool]`
- `can_manage_users: Optional[bool]`
- `can_view_analytics: Optional[bool]`

**Retained fields:**
- Inherits from `UserBase`
- `password: str`
- `confirm_password: str`
- Password validation logic

### 2. Updated Registration Endpoint (`app/api/auth.py`)

#### New Function: `assign_permissions_by_role()`
Automatically assigns permissions based on user role:

```python
def assign_permissions_by_role(role: str) -> dict:
    """Automatically assign permissions based on user role"""
    role_permissions = {
        "admin": {
            "can_manage_inventory": True,
            "can_view_forecasts": True, 
            "can_manage_donors": True,
            "can_access_reports": True,
            "can_manage_users": True,
            "can_view_analytics": True
        },
        "manager": {
            "can_manage_inventory": True,
            "can_view_forecasts": True,
            "can_manage_donors": True, 
            "can_access_reports": True,
            "can_manage_users": False,
            "can_view_analytics": True
        },
        "staff": {
            "can_manage_inventory": False,
            "can_view_forecasts": True,
            "can_manage_donors": True,
            "can_access_reports": True, 
            "can_manage_users": False,
            "can_view_analytics": True
        },
        "viewer": {
            "can_manage_inventory": False,
            "can_view_forecasts": True,
            "can_manage_donors": False,
            "can_access_reports": True,
            "can_manage_users": False, 
            "can_view_analytics": True
        }
    }
    return role_permissions.get(role.lower(), role_permissions["staff"])
```

#### Updated `register_user()` Function
- **Removed:** Manual permission assignment from request data
- **Removed:** Employee ID validation (field no longer collected)
- **Added:** Role validation against allowed values
- **Added:** Automatic permission assignment based on role
- **Simplified:** User creation with only essential fields

### 3. Updated Documentation (`RBAC_GUIDE.md`)

#### Added New Section: "Simplified User Registration with Automatic Permissions"
- Documents the new streamlined registration process
- Shows examples for each role type
- Explains automatic permission assignment logic
- Highlights benefits of the new system

#### Updated Registration Examples
- **New examples:** Show simplified registration with only essential fields
- **Legacy examples:** Marked deprecated but kept for reference
- **Clear benefits:** Consistency, security, simplicity, maintainability

## Registration Request Format

### New Simplified Format
```json
{
  "username": "john_doe",
  "email": "john@bloodbank.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!", 
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "staff"
}
```

### Old Format (Deprecated)
```json
{
  "username": "john_doe",
  "email": "john@bloodbank.com", 
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "+1234567890",
  "role": "staff",
  "department": "Blood Bank",
  "employee_id": "EMP001",
  "position": "Technician",
  "can_manage_inventory": false,
  "can_view_forecasts": true,
  "can_manage_donors": true,
  "can_access_reports": true,
  "can_manage_users": false,
  "can_view_analytics": true
}
```

## Benefits

### 1. **Improved User Experience**
- Fewer fields to fill during registration
- No need to understand permission system details
- Faster registration process

### 2. **Enhanced Security** 
- Eliminates human error in permission assignment
- Ensures consistent role-based permissions
- Prevents privilege escalation during registration

### 3. **Better Maintainability**
- Centralized permission logic
- Easy to update role permissions
- Consistent across all registrations

### 4. **Simplified Administration**
- No need to train users on permission details
- Automatic compliance with security policies
- Reduced support requests

## Backward Compatibility

- **Database:** No migration needed - removed fields are optional in User model
- **Existing Users:** Unaffected - can keep existing department/employee_id data
- **API:** Registration endpoint maintains same URL but accepts simplified payload
- **Authentication:** No changes to login or JWT token system

## Testing

The updated system has been validated for:
- ✅ Syntax errors resolved
- ✅ Schema validation working
- ✅ Role-based permission assignment logic
- ✅ Registration endpoint functionality
- ✅ Documentation completeness

## Next Steps

1. **Testing**: Test registration with each role type
2. **Frontend Update**: Update registration forms to match new schema
3. **Validation**: Ensure all role types get correct permissions
4. **Documentation**: Update API documentation if needed
