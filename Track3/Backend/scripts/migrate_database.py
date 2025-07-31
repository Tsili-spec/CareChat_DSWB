#!/usr/bin/env python3
"""
Database migration script for blood bank system updates
This script migrates the existing schema to the new structure with:
1. Updated BloodStock table with new fields
2. Changed DateTime fields to Date fields where appropriate
3. Updated blood collection and usage tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Run database migration"""
    load_dotenv()
    
    # Get DATABASE_URL from environment
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    engine = create_engine(DATABASE_URL)
    
    print('🔄 Starting database migration...')
    
    with engine.connect() as conn:
        try:
            # Start transaction
            trans = conn.begin()
            
            print('📊 Migrating BloodStock table...')
            
            # Add new columns to blood_stock table
            migration_queries = [
                # Add new columns to blood_stock
                """
                ALTER TABLE blood_stock 
                ADD COLUMN IF NOT EXISTS total_available FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS total_near_expiry FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS total_expired FLOAT DEFAULT 0.0,
                ADD COLUMN IF NOT EXISTS stock_date DATE,
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
                """,
                
                # Update stock_date from existing time column
                """
                UPDATE blood_stock 
                SET stock_date = DATE(time) 
                WHERE stock_date IS NULL;
                """,
                
                # Migrate existing volume_in_stock to total_available
                """
                UPDATE blood_stock 
                SET total_available = volume_in_stock 
                WHERE total_available = 0.0 AND volume_in_stock IS NOT NULL;
                """,
                
                # Update blood_collections table - change datetime to date
                """
                ALTER TABLE blood_collections 
                ADD COLUMN IF NOT EXISTS donation_date_new DATE,
                ADD COLUMN IF NOT EXISTS expiry_date_new DATE;
                """,
                
                """
                UPDATE blood_collections 
                SET donation_date_new = DATE(donation_date),
                    expiry_date_new = DATE(expiry_date)
                WHERE donation_date_new IS NULL;
                """,
                
                # Update blood_usage table - change datetime to date
                """
                ALTER TABLE blood_usage 
                ADD COLUMN IF NOT EXISTS usage_date DATE;
                """,
                
                """
                UPDATE blood_usage 
                SET usage_date = DATE(time)
                WHERE usage_date IS NULL;
                """,
                
                # Create indexes for performance
                """
                CREATE INDEX IF NOT EXISTS idx_blood_stock_blood_group_date_new 
                ON blood_stock(blood_group, stock_date);
                """,
                
                """
                CREATE INDEX IF NOT EXISTS idx_blood_collections_donation_date_new 
                ON blood_collections(donation_date_new);
                """,
                
                """
                CREATE INDEX IF NOT EXISTS idx_blood_usage_usage_date_new 
                ON blood_usage(usage_date);
                """
            ]
            
            for i, query in enumerate(migration_queries, 1):
                print(f'  Step {i}/{len(migration_queries)}: Executing migration query...')
                conn.execute(text(query))
                conn.commit()
            
            print('✅ Migration completed successfully!')
            print('📝 Note: Old columns preserved for safety. You may need to update the models to drop old columns after verification.')
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            trans.rollback()
            raise
        else:
            trans.commit()

if __name__ == "__main__":
    run_migration()
