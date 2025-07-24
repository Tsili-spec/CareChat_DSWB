#!/usr/bin/env python3
"""
User management script to clean up users
- Get list of all users
- Delete users whose full name is not "Asongna Frank"
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_all_users():
    """Get all users from the API"""
    try:
        response = requests.get(f"{BASE_URL}/api/patients")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error getting users: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return None

def delete_user(patient_id):
    """Delete a user by patient_id"""
    try:
        response = requests.delete(f"{BASE_URL}/api/patients/{patient_id}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error deleting user {patient_id}: {str(e)}")
        return False

def main():
    print("🧹 Starting user cleanup process...")
    print(f"📍 Target: Keep only users with full name 'Asongna Frank'")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Get all users
    print("📋 Fetching all users...")
    users = get_all_users()
    
    if users is None:
        print("❌ Failed to get users. Exiting.")
        return
    
    print(f"📊 Found {len(users)} total users")
    
    # Find users to keep and delete
    users_to_keep = []
    users_to_delete = []
    
    for user in users:
        full_name = user.get('full_name', '')
        patient_id = user.get('patient_id', '')
        email = user.get('email', '')
        
        if full_name == "Asongna Frank":
            users_to_keep.append(user)
            print(f"✅ KEEP - {full_name} (ID: {patient_id}, Email: {email})")
        else:
            users_to_delete.append(user)
            print(f"🗑️  DELETE - {full_name} (ID: {patient_id}, Email: {email})")
    
    print("\n" + "=" * 60)
    print(f"📈 SUMMARY:")
    print(f"  Users to keep: {len(users_to_keep)}")
    print(f"  Users to delete: {len(users_to_delete)}")
    
    if len(users_to_delete) == 0:
        print("✨ No users need to be deleted. All users are 'Asongna Frank' or no users found.")
        return
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: About to delete {len(users_to_delete)} users!")
    print("Users to be deleted:")
    for user in users_to_delete:
        print(f"  - {user.get('full_name', 'Unknown')} ({user.get('email', 'No email')})")
    
    confirmation = input("\n🤔 Do you want to proceed with deletion? (yes/no): ").lower().strip()
    
    if confirmation != 'yes':
        print("❌ Deletion cancelled by user.")
        return
    
    # Proceed with deletion
    print(f"\n🗑️  Proceeding with deletion of {len(users_to_delete)} users...")
    
    deleted_count = 0
    failed_count = 0
    
    for user in users_to_delete:
        patient_id = user.get('patient_id', '')
        full_name = user.get('full_name', 'Unknown')
        
        print(f"Deleting: {full_name} (ID: {patient_id})...", end=' ')
        
        if delete_user(patient_id):
            deleted_count += 1
            print("✅ SUCCESS")
        else:
            failed_count += 1
            print("❌ FAILED")
    
    # Final summary
    print("\n" + "=" * 60)
    print(f"🏁 CLEANUP COMPLETED")
    print(f"✅ Successfully deleted: {deleted_count}")
    print(f"❌ Failed to delete: {failed_count}")
    print(f"👥 Remaining users: {len(users_to_keep)}")
    print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if len(users_to_keep) > 0:
        print(f"\n📋 Remaining users:")
        for user in users_to_keep:
            print(f"  - {user.get('full_name', 'Unknown')} ({user.get('email', 'No email')})")

if __name__ == "__main__":
    main()
