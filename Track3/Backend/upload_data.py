#!/usr/bin/env python3
"""
Data Upload Script for Blood Bank System
Uploads data from CSV files to the database through API endpoints
"""

import pandas as pd
import requests
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BloodBankDataUploader:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        
    def authenticate(self, username: str = "frank", password: str = "Frank123") -> bool:
        """
        Authenticate with the API and get JWT token
        """
        try:
            # Try to login with admin credentials
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def create_admin_user(self) -> bool:
        """
        Create an admin user if authentication fails
        """
        try:
            user_data = {
                "username": "frank",
                "email": "frank@bloodbank.com",
                "password": "Frank123",
                "confirm_password": "Frank123",
                "full_name": "Frank Admin",
                "role": "admin"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code in [200, 201]:
                logger.info("Admin user created successfully")
                return True
            else:
                logger.error(f"Failed to create admin user: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            return False
    
    def clean_collection_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare blood collection data
        """
        logger.info("Cleaning blood collection data...")
        
        # Drop rows with missing critical data
        df_clean = df.dropna(subset=['donor_age', 'donor_gender', 'blood_type'])
        
        # Fill missing values
        df_clean['collection_site'] = df_clean['collection_site'].fillna('Unknown Site')
        df_clean['donor_occupation'] = df_clean.get('donor_occupation', 'Unknown')
        
        # Handle dates
        df_clean['donation_date'] = pd.to_datetime(df_clean['donation_date'], errors='coerce')
        df_clean['expiry_date'] = pd.to_datetime(df_clean['expiry_date'], errors='coerce')
        
        # Fill missing donation dates with a default
        df_clean['donation_date'] = df_clean['donation_date'].fillna(datetime.now().date())
        
        # Calculate expiry date if missing (45 days from donation)
        df_clean['expiry_date'] = df_clean['expiry_date'].fillna(
            df_clean['donation_date'] + timedelta(days=45)
        )
        
        # Clean volume and hemoglobin data
        df_clean['collection_volume_ml'] = pd.to_numeric(df_clean['collection_volume_ml'], errors='coerce')
        df_clean['hemoglobin_g_dl'] = pd.to_numeric(df_clean['hemoglobin_g_dl'], errors='coerce')
        
        # Fill missing values with reasonable defaults
        df_clean['collection_volume_ml'] = df_clean['collection_volume_ml'].fillna(450.0)
        df_clean['hemoglobin_g_dl'] = df_clean['hemoglobin_g_dl'].fillna(13.5)
        
        # Filter out invalid data
        df_clean = df_clean[
            (df_clean['donor_age'] >= 18) & 
            (df_clean['donor_age'] <= 70) &
            (df_clean['collection_volume_ml'] > 0) &
            (df_clean['collection_volume_ml'] <= 500) &
            (df_clean['hemoglobin_g_dl'] > 0) &
            (df_clean['hemoglobin_g_dl'] <= 20)
        ]
        
        logger.info(f"Cleaned data: {len(df_clean)} valid records from {len(df)} total")
        return df_clean
    
    def clean_usage_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare blood usage data
        """
        logger.info("Cleaning blood usage data...")
        
        # Drop rows with missing critical data
        df_clean = df.dropna(subset=['purpose', 'department', 'blood_group', 'volume_given_out'])
        
        # Clean and validate data
        df_clean['usage_date'] = pd.to_datetime(df_clean['usage_date'], errors='coerce')
        df_clean['usage_date'] = df_clean['usage_date'].fillna(datetime.now().date())
        
        df_clean['volume_given_out'] = pd.to_numeric(df_clean['volume_given_out'], errors='coerce')
        df_clean = df_clean[
            (df_clean['volume_given_out'] > 0) & 
            (df_clean['volume_given_out'] <= 5000)  # Reasonable upper limit
        ]
        
        # Fill missing individual names
        df_clean['individual_name'] = df_clean['individual_name'].fillna('Unknown Patient')
        df_clean['patient_location'] = df_clean['patient_location'].fillna('Unknown Location')
        
        logger.info(f"Cleaned usage data: {len(df_clean)} valid records from {len(df)} total")
        return df_clean
    
    def upload_collections(self, csv_file: str, batch_size: int = 100) -> bool:
        """
        Upload blood collection data from CSV file
        """
        try:
            logger.info(f"Reading collection data from {csv_file}")
            df = pd.read_csv(csv_file)
            df_clean = self.clean_collection_data(df)
            
            total_records = len(df_clean)
            successful_uploads = 0
            failed_uploads = 0
            
            logger.info(f"Starting upload of {total_records} collection records...")
            
            for index, row in df_clean.iterrows():
                try:
                    collection_data = {
                        "donor_age": int(row['donor_age']),
                        "donor_gender": row['donor_gender'],
                        "donor_occupation": str(row.get('donor_occupation', 'Unknown')),
                        "blood_type": row['blood_type'],
                        "collection_site": str(row['collection_site']),
                        "donation_date": row['donation_date'].strftime('%Y-%m-%d'),
                        "expiry_date": row['expiry_date'].strftime('%Y-%m-%d'),
                        "collection_volume_ml": float(row['collection_volume_ml']),
                        "hemoglobin_g_dl": float(row['hemoglobin_g_dl'])
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/v1/blood-bank/collections",
                        json=collection_data
                    )
                    
                    if response.status_code in [200, 201]:
                        successful_uploads += 1
                        if successful_uploads % 50 == 0:
                            logger.info(f"Uploaded {successful_uploads}/{total_records} collections...")
                    else:
                        failed_uploads += 1
                        logger.warning(f"Failed to upload collection {index}: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    failed_uploads += 1
                    logger.error(f"Error uploading collection {index}: {e}")
            
            logger.info(f"Collection upload complete: {successful_uploads} successful, {failed_uploads} failed")
            return failed_uploads == 0
            
        except Exception as e:
            logger.error(f"Error uploading collections: {e}")
            return False
    
    def upload_usage(self, csv_file: str, batch_size: int = 100) -> bool:
        """
        Upload blood usage data from CSV file
        """
        try:
            logger.info(f"Reading usage data from {csv_file}")
            df = pd.read_csv(csv_file)
            df_clean = self.clean_usage_data(df)
            
            total_records = len(df_clean)
            successful_uploads = 0
            failed_uploads = 0
            
            logger.info(f"Starting upload of {total_records} usage records...")
            
            for index, row in df_clean.iterrows():
                try:
                    usage_data = {
                        "purpose": str(row['purpose']),
                        "department": str(row['department']),
                        "blood_group": row['blood_group'],
                        "volume_given_out": float(row['volume_given_out']),
                        "usage_date": row['usage_date'].strftime('%Y-%m-%d'),
                        "individual_name": str(row['individual_name']),
                        "patient_location": str(row['patient_location'])
                    }
                    
                    response = self.session.post(
                        f"{self.base_url}/api/v1/blood-bank/usage",
                        json=usage_data
                    )
                    
                    if response.status_code in [200, 201]:
                        successful_uploads += 1
                        if successful_uploads % 50 == 0:
                            logger.info(f"Uploaded {successful_uploads}/{total_records} usage records...")
                    else:
                        failed_uploads += 1
                        logger.warning(f"Failed to upload usage {index}: {response.status_code} - {response.text}")
                        
                except Exception as e:
                    failed_uploads += 1
                    logger.error(f"Error uploading usage {index}: {e}")
            
            logger.info(f"Usage upload complete: {successful_uploads} successful, {failed_uploads} failed")
            return failed_uploads == 0
            
        except Exception as e:
            logger.error(f"Error uploading usage data: {e}")
            return False

def main():
    """
    Main function to run the data upload process
    """
    # Set up paths
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data"
    collections_file = data_dir / "blood_bank_records.csv"
    usage_file = data_dir / "usage_data.csv"
    
    # Check if files exist
    if not collections_file.exists():
        logger.error(f"Collections file not found: {collections_file}")
        return False
    
    if not usage_file.exists():
        logger.error(f"Usage file not found: {usage_file}")
        return False
    
    # Create uploader instance
    uploader = BloodBankDataUploader()
    
    # Try to authenticate
    if not uploader.authenticate():
        logger.info("Authentication failed, trying to create admin user...")
        if not uploader.create_admin_user():
            logger.error("Failed to create admin user. Please create one manually.")
            return False
        
        # Try to authenticate again
        if not uploader.authenticate():
            logger.error("Authentication still failed after creating admin user")
            return False
    
    # Upload data
    logger.info("Starting data upload process...")
    
    # Upload collections first
    logger.info("=" * 50)
    logger.info("UPLOADING BLOOD COLLECTIONS")
    logger.info("=" * 50)
    collections_success = uploader.upload_collections(str(collections_file))
    
    # Upload usage data
    logger.info("=" * 50)
    logger.info("UPLOADING BLOOD USAGE DATA")
    logger.info("=" * 50)
    usage_success = uploader.upload_usage(str(usage_file))
    
    # Summary
    logger.info("=" * 50)
    logger.info("UPLOAD SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Collections upload: {'SUCCESS' if collections_success else 'FAILED'}")
    logger.info(f"Usage upload: {'SUCCESS' if usage_success else 'FAILED'}")
    
    if collections_success and usage_success:
        logger.info("All data uploaded successfully!")
        return True
    else:
        logger.error("Some uploads failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
