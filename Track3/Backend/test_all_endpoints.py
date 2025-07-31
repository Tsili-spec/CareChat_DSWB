#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Blood Bank Management System
Tests all endpoints with proper error handling and output formatting
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8001/api/v1"

class APITester:
    def __init__(self):
        self.access_token = None
        self.user_id = None
        self.session = requests.Session()
        
    def test_endpoint(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     headers: Optional[Dict] = None, description: str = "") -> Dict[str, Any]:
        """Test an API endpoint and return results"""
        print(f"\n{'='*60}")
        print(f"Testing: {description}")
        print(f"Method: {method.upper()} {endpoint}")
        
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method.lower() == 'get':
                response = self.session.get(url, headers=headers)
            elif method.lower() == 'post':
                response = self.session.post(url, json=data, headers=headers)
            elif method.lower() == 'put':
                response = self.session.put(url, json=data, headers=headers)
            elif method.lower() == 'delete':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            print(f"Status Code: {response.status_code}")
            
            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
                return {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "data": response_data
                }
            except json.JSONDecodeError:
                print(f"Response (text): {response.text}")
                return {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "data": response.text
                }
                
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                "success": False,
                "status_code": None,
                "error": str(e)
            }
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if not self.access_token:
            raise ValueError("No access token available. Please login first.")
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n" + "="*80)
        print("TESTING AUTHENTICATION ENDPOINTS")
        print("="*80)
        
        # Test Login
        login_data = {
            "username": "testadmin",
            "password": "TestPass123!"
        }
        
        result = self.test_endpoint(
            "POST", "/auth/login", 
            data=login_data,
            description="User Login"
        )
        
        if result["success"]:
            self.access_token = result["data"].get("access_token")
            self.user_id = result["data"].get("user_id")
            print(f"✅ Login successful! User ID: {self.user_id}")
        else:
            print("❌ Login failed!")
            return False
            
        # Test getting current user info
        result = self.test_endpoint(
            "GET", "/auth/me",
            headers=self.get_auth_headers(),
            description="Get Current User Info"
        )
        
        if result["success"]:
            print("✅ Get current user successful!")
        else:
            print("❌ Get current user failed!")
            
        # Test change password
        change_password_data = {
            "current_password": "TestPass123!",
            "new_password": "NewTestPass123!",
            "confirm_password": "NewTestPass123!"
        }
        
        result = self.test_endpoint(
            "POST", "/auth/change-password",
            data=change_password_data,
            headers=self.get_auth_headers(),
            description="Change Password"
        )
        
        if result["success"]:
            print("✅ Change password successful!")
            
            # Change it back
            change_back_data = {
                "current_password": "NewTestPass123!",
                "new_password": "TestPass123!",
                "confirm_password": "TestPass123!"
            }
            
            self.test_endpoint(
                "POST", "/auth/change-password",
                data=change_back_data,
                headers=self.get_auth_headers(),
                description="Change Password Back"
            )
        else:
            print("❌ Change password failed!")
            
        return True
    
    def test_user_management(self):
        """Test user management endpoints"""
        print("\n" + "="*80)
        print("TESTING USER MANAGEMENT ENDPOINTS")
        print("="*80)
        
        # Test list all users
        result = self.test_endpoint(
            "GET", "/auth/users",
            headers=self.get_auth_headers(),
            description="List All Users"
        )
        
        if result["success"]:
            print("✅ List users successful!")
        else:
            print("❌ List users failed!")
            
        # Test get user by ID
        if self.user_id:
            result = self.test_endpoint(
                "GET", f"/auth/users/{self.user_id}",
                headers=self.get_auth_headers(),
                description=f"Get User by ID ({self.user_id})"
            )
            
            if result["success"]:
                print("✅ Get user by ID successful!")
            else:
                print("❌ Get user by ID failed!")
                
        # Test create new user
        new_user_data = {
            "username": "teststaff",
            "email": "staff@test.com",
            "full_name": "Test Staff Member",
            "password": "StaffPass123!",
            "confirm_password": "StaffPass123!",
            "role": "staff"
        }
        
        result = self.test_endpoint(
            "POST", "/auth/register",
            data=new_user_data,
            description="Register New Staff User"
        )
        
        new_user_id = None
        if result["success"]:
            print("✅ Register new user successful!")
            new_user_id = result["data"].get("user_id")
        elif result["status_code"] == 400 and "already registered" in str(result["data"]):
            print("✅ User already exists (expected for repeated tests)")
            
            # Try to find the existing user
            users_result = self.test_endpoint(
                "GET", "/auth/users",
                headers=self.get_auth_headers(),
                description="Get existing staff user"
            )
            
            if users_result["success"]:
                for user in users_result["data"]:
                    if user["username"] == "teststaff":
                        new_user_id = user["user_id"]
                        break
        else:
            print("❌ Register new user failed!")
            
        # Test update user (if we have a staff user ID)
        if new_user_id:
            update_data = {
                "full_name": "Updated Test Staff Member",
                "role": "staff"
            }
            
            result = self.test_endpoint(
                "PUT", f"/auth/users/{new_user_id}",
                data=update_data,
                headers=self.get_auth_headers(),
                description=f"Update User ({new_user_id})"
            )
            
            if result["success"]:
                print("✅ Update user successful!")
            else:
                print("❌ Update user failed!")
    
    def test_blood_bank_endpoints(self):
        """Test blood bank management endpoints"""
        print("\n" + "="*80)
        print("TESTING BLOOD BANK ENDPOINTS")
        print("="*80)
        
        # Test create blood collection
        collection_data = {
            "blood_type": "O+",
            "units_collected": 2,
            "collection_date": "2025-07-31",
            "expiry_date": "2025-08-31",
            "collection_center": "Main Hospital",
            "storage_location": "Fridge A1"
        }
        
        result = self.test_endpoint(
            "POST", "/blood-bank/collections",
            data=collection_data,
            headers=self.get_auth_headers(),
            description="Create Blood Collection"
        )
        
        collection_id = None
        if result["success"]:
            print("✅ Create blood collection successful!")
            collection_id = result["data"].get("collection_id")
        else:
            print("❌ Create blood collection failed!")
            
        # Test get all collections
        result = self.test_endpoint(
            "GET", "/blood-bank/collections",
            headers=self.get_auth_headers(),
            description="Get All Blood Collections"
        )
        
        if result["success"]:
            print("✅ Get all collections successful!")
        else:
            print("❌ Get all collections failed!")
            
        # Test get collection by ID
        if collection_id:
            result = self.test_endpoint(
                "GET", f"/blood-bank/collections/{collection_id}",
                headers=self.get_auth_headers(),
                description=f"Get Collection by ID ({collection_id})"
            )
            
            if result["success"]:
                print("✅ Get collection by ID successful!")
            else:
                print("❌ Get collection by ID failed!")
                
        # Test create blood usage
        usage_data = {
            "blood_type": "O+",
            "units_used": 1,
            "usage_date": "2025-07-31",
            "hospital_name": "City General Hospital",
            "patient_info": "Emergency surgery - anonymized"
        }
        
        result = self.test_endpoint(
            "POST", "/blood-bank/usage",
            data=usage_data,
            headers=self.get_auth_headers(),
            description="Create Blood Usage"
        )
        
        usage_id = None
        if result["success"]:
            print("✅ Create blood usage successful!")
            usage_id = result["data"].get("usage_id")
        else:
            print("❌ Create blood usage failed!")
            
        # Test get all usage records
        result = self.test_endpoint(
            "GET", "/blood-bank/usage",
            headers=self.get_auth_headers(),
            description="Get All Blood Usage Records"
        )
        
        if result["success"]:
            print("✅ Get all usage records successful!")
        else:
            print("❌ Get all usage records failed!")
            
        # Test get usage by ID
        if usage_id:
            result = self.test_endpoint(
                "GET", f"/blood-bank/usage/{usage_id}",
                headers=self.get_auth_headers(),
                description=f"Get Usage by ID ({usage_id})"
            )
            
            if result["success"]:
                print("✅ Get usage by ID successful!")
            else:
                print("❌ Get usage by ID failed!")
                
        # Test get stock summary
        result = self.test_endpoint(
            "GET", "/blood-bank/stock",
            headers=self.get_auth_headers(),
            description="Get Stock Summary"
        )
        
        if result["success"]:
            print("✅ Get stock summary successful!")
        else:
            print("❌ Get stock summary failed!")
            
        # Test get stock by blood type
        result = self.test_endpoint(
            "GET", "/blood-bank/stock/O+",
            headers=self.get_auth_headers(),
            description="Get Stock for Blood Type O+"
        )
        
        if result["success"]:
            print("✅ Get stock by blood type successful!")
        else:
            print("❌ Get stock by blood type failed!")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("Starting comprehensive API testing...")
        print(f"Base URL: {BASE_URL}")
        
        try:
            # Test authentication first
            if not self.test_authentication():
                print("❌ Authentication tests failed. Stopping.")
                return False
                
            # Test user management
            self.test_user_management()
            
            # Test blood bank endpoints
            self.test_blood_bank_endpoints()
            
            print("\n" + "="*80)
            print("🎉 ALL TESTS COMPLETED!")
            print("="*80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
