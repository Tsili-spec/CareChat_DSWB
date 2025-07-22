#!/usr/bin/env python3
import sqlite3
import sys
import os

# Change to Backend directory
os.chdir('/home/asongna/Desktop/Carechat/Track2/Backend')

try:
    conn = sqlite3.connect('carechat.db')
    cursor = conn.cursor()
    
    # Get table structure
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    print("=== USERS TABLE STRUCTURE ===")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")
    
    # Get all users
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]
    print(f"\n=== USERS COUNT: {count} ===")
    
    if count > 0:
        cursor.execute("SELECT patient_id, full_name, phone_number, email, preferred_language FROM users;")
        users = cursor.fetchall()
        print("=== USER RECORDS ===")
        for user in users:
            print(f"  ID: {user[0]}")
            print(f"  Name: {user[1]}")
            print(f"  Phone: {user[2]}")
            print(f"  Email: {user[3]}")
            print(f"  Language: {user[4]}")
            print("  ---")
    
    conn.close()
    print("✅ Database check completed successfully")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
