#!/usr/bin/env python3
"""
Script to display the current database schema.
Shows all tables, columns, data types, constraints, etc.
"""

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.core.config import settings
import sys

def get_database_schema():
    """Get and display the current database schema"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔍 Analyzing database schema...")
            print(f"📍 Database: {settings.DATABASE_URL.split('@')[-1].split('/')[1] if '@' in settings.DATABASE_URL else 'Unknown'}")
            print("=" * 80)
            
            # Get all tables
            tables_result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in tables_result]
            
            if not tables:
                print("❌ No tables found in the database.")
                return
            
            print(f"📋 Found {len(tables)} tables\n")
            
            # For each table, get detailed information
            for table_name in tables:
                print(f"📄 TABLE: {table_name}")
                print("-" * 60)
                
                # Get columns information
                columns_result = conn.execute(text("""
                    SELECT 
                        column_name,
                        data_type,
                        character_maximum_length,
                        is_nullable,
                        column_default,
                        ordinal_position
                    FROM information_schema.columns 
                    WHERE table_name = :table_name 
                    AND table_schema = 'public'
                    ORDER BY ordinal_position
                """), {"table_name": table_name})
                
                columns = list(columns_result)
                
                if columns:
                    print(f"   Columns ({len(columns)}):")
                    for col in columns:
                        col_name, data_type, max_length, nullable, default, position = col
                        
                        # Format data type
                        if max_length:
                            type_info = f"{data_type}({max_length})"
                        else:
                            type_info = data_type
                        
                        # Format nullable
                        null_info = "NULL" if nullable == "YES" else "NOT NULL"
                        
                        # Format default
                        default_info = f"DEFAULT {default}" if default else ""
                        
                        print(f"     {position:2}. {col_name:<20} {type_info:<15} {null_info:<8} {default_info}")
                
                # Get primary keys
                pk_result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.key_column_usage
                    WHERE table_name = :table_name
                    AND table_schema = 'public'
                    AND constraint_name IN (
                        SELECT constraint_name
                        FROM information_schema.table_constraints
                        WHERE table_name = :table_name
                        AND table_schema = 'public'
                        AND constraint_type = 'PRIMARY KEY'
                    )
                """), {"table_name": table_name})
                
                primary_keys = [row[0] for row in pk_result]
                if primary_keys:
                    print(f"   🔑 Primary Key(s): {', '.join(primary_keys)}")
                
                # Get foreign keys
                fk_result = conn.execute(text("""
                    SELECT 
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.key_column_usage AS kcu
                    INNER JOIN information_schema.referential_constraints AS rc
                        ON kcu.constraint_name = rc.constraint_name
                    INNER JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = rc.unique_constraint_name
                    WHERE kcu.table_name = :table_name
                    AND kcu.table_schema = 'public'
                """), {"table_name": table_name})
                
                foreign_keys = list(fk_result)
                if foreign_keys:
                    print("   🔗 Foreign Key(s):")
                    for fk in foreign_keys:
                        col_name, ref_table, ref_col = fk
                        print(f"     {col_name} → {ref_table}.{ref_col}")
                
                # Get indexes
                indexes_result = conn.execute(text("""
                    SELECT 
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE tablename = :table_name
                    AND schemaname = 'public'
                """), {"table_name": table_name})
                
                indexes = list(indexes_result)
                if indexes:
                    print("   📇 Indexes:")
                    for idx in indexes:
                        idx_name, idx_def = idx
                        print(f"     {idx_name}")
                
                # Get row count
                try:
                    count_result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
                    row_count = count_result.scalar()
                    print(f"   📊 Row Count: {row_count}")
                except Exception as e:
                    print(f"   📊 Row Count: Unable to count ({str(e)[:50]}...)")
                
                print()  # Empty line between tables
            
            # Get database size information
            try:
                size_result = conn.execute(text("""
                    SELECT 
                        pg_size_pretty(pg_database_size(current_database())) as db_size
                """))
                db_size = size_result.scalar()
                print(f"💾 Database Size: {db_size}")
            except Exception as e:
                print(f"💾 Database Size: Unable to determine ({str(e)[:50]}...)")
            
            print("\n" + "=" * 80)
            print("✅ Schema analysis complete!")
            
    except Exception as e:
        print(f"❌ Error analyzing schema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 80)
    print("🗃️  DATABASE SCHEMA ANALYZER")
    print("=" * 80)
    
    # Load environment variables
    load_dotenv()
    
    if not settings.DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables!")
        sys.exit(1)
    
    success = get_database_schema()
    
    if not success:
        sys.exit(1)
