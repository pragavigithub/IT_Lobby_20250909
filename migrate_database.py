#!/usr/bin/env python3
"""
Database Migration Script for Serial Item Transfer Enhancement
This script adds the new columns required for the enhanced Serial Item Transfer workflow
"""

import sys
import logging
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import application modules
from credential_loader import load_credentials
import pymysql

def setup_logging():
    """Setup logging for migration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('migration.log')
        ]
    )
    return logging.getLogger(__name__)

def get_database_connection():
    """Get database connection using credentials"""
    logger = logging.getLogger(__name__)
    
    try:
        # Load credentials
        creds = load_credentials()
        
        # Use MySQL credentials from JSON file
        connection = pymysql.connect(
            host=creds.get('MYSQL_HOST', 'localhost'),
            port=int(creds.get('MYSQL_PORT', 3306)),
            user=creds.get('MYSQL_USER', 'root'),
            password=creds.get('MYSQL_PASSWORD', ''),
            database=creds.get('MYSQL_DATABASE', 'it_lobby'),
            charset='utf8mb4',
            autocommit=False
        )
        
        logger.info("✅ Connected to MySQL database successfully")
        return connection
        
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        return None

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in the table"""
    query = """
    SELECT COUNT(*) as count
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
    AND TABLE_NAME = %s 
    AND COLUMN_NAME = %s
    """
    cursor.execute(query, (table_name, column_name))
    result = cursor.fetchone()
    return result['count'] > 0

def run_migration():
    """Run the database migration"""
    logger = setup_logging()
    logger.info("🚀 Starting Serial Item Transfer Enhancement Migration")
    
    # Get database connection
    connection = get_database_connection()
    if not connection:
        logger.error("Cannot proceed without database connection")
        return False
    
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Check if migration is needed
        table_name = 'serial_item_transfer_items'
        columns_to_add = [
            ('is_serial_managed', 'BOOLEAN NOT NULL DEFAULT FALSE'),
            ('is_batch_managed', 'BOOLEAN NOT NULL DEFAULT FALSE'),
            ('item_type', 'VARCHAR(20) NOT NULL DEFAULT \'serial\''),
            ('expected_quantity', 'INT NOT NULL DEFAULT 1'),
            ('scanned_quantity', 'INT NOT NULL DEFAULT 0'),
            ('completion_status', 'VARCHAR(20) NOT NULL DEFAULT \'pending\''),
            ('parent_item_code', 'VARCHAR(50) NULL'),
            ('line_group_id', 'VARCHAR(50) NULL')
        ]
        
        logger.info(f"📋 Checking table: {table_name}")
        
        # Check which columns need to be added
        columns_needed = []
        for column_name, column_def in columns_to_add:
            if not check_column_exists(cursor, table_name, column_name):
                columns_needed.append((column_name, column_def))
                logger.info(f"  📌 Column '{column_name}' needs to be added")
            else:
                logger.info(f"  ✅ Column '{column_name}' already exists")
        
        if not columns_needed:
            logger.info("🎉 All required columns already exist! No migration needed.")
            return True
        
        # Add missing columns
        logger.info(f"📝 Adding {len(columns_needed)} missing columns...")
        
        for column_name, column_def in columns_needed:
            try:
                alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
                logger.info(f"  🔧 Adding column: {column_name}")
                cursor.execute(alter_query)
                logger.info(f"  ✅ Successfully added column: {column_name}")
            except Exception as e:
                logger.error(f"  ❌ Failed to add column {column_name}: {e}")
                raise
        
        # Make serial_number nullable
        try:
            logger.info("🔧 Making serial_number column nullable...")
            cursor.execute(f"ALTER TABLE {table_name} MODIFY COLUMN serial_number VARCHAR(100) NULL")
            logger.info("✅ Successfully made serial_number nullable")
        except Exception as e:
            logger.warning(f"⚠️  Warning: Could not modify serial_number column: {e}")
        
        # Update existing records with proper defaults
        logger.info("📊 Updating existing records with proper defaults...")
        
        # Update records with serial numbers
        cursor.execute(f"""
            UPDATE {table_name} 
            SET 
                is_serial_managed = TRUE,
                item_type = 'serial',
                expected_quantity = 1,
                scanned_quantity = CASE 
                    WHEN serial_number IS NOT NULL AND serial_number != '' THEN 1 
                    ELSE 0 
                END,
                completion_status = CASE 
                    WHEN serial_number IS NOT NULL AND serial_number != '' THEN 'completed' 
                    ELSE 'pending' 
                END
            WHERE serial_number IS NOT NULL AND serial_number != ''
        """)
        
        # Update records without serial numbers
        cursor.execute(f"""
            UPDATE {table_name} 
            SET 
                is_serial_managed = FALSE,
                item_type = 'non_serial',
                expected_quantity = COALESCE(quantity, 1),
                scanned_quantity = COALESCE(quantity, 1),
                completion_status = 'completed'
            WHERE serial_number IS NULL OR serial_number = ''
        """)
        
        logger.info("✅ Successfully updated existing records")
        
        # Create useful indexes
        logger.info("🔍 Creating performance indexes...")
        indexes = [
            f"CREATE INDEX idx_{table_name}_is_serial_managed ON {table_name}(is_serial_managed)",
            f"CREATE INDEX idx_{table_name}_completion_status ON {table_name}(completion_status)",
            f"CREATE INDEX idx_{table_name}_item_type ON {table_name}(item_type)"
        ]
        
        for index_query in indexes:
            try:
                cursor.execute(index_query)
                logger.info(f"  ✅ Created index successfully")
            except Exception as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    logger.info(f"  ℹ️  Index already exists (skipping)")
                else:
                    logger.warning(f"  ⚠️  Warning: Could not create index: {e}")
        
        # Commit all changes
        connection.commit()
        logger.info("💾 Committed all changes to database")
        
        # Verify migration
        logger.info("🔍 Verifying migration...")
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        record_count = cursor.fetchone()['count']
        logger.info(f"✅ Table {table_name} has {record_count} records")
        
        logger.info("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        connection.rollback()
        logger.info("🔄 Rolled back all changes")
        return False
        
    finally:
        if connection:
            connection.close()
            logger.info("🔒 Database connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("Serial Item Transfer Enhancement Database Migration")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    if success:
        print("✅ Migration completed successfully!")
        print("You can now run your application without errors.")
    else:
        print("❌ Migration failed!")
        print("Please check the migration.log file for details.")
    
    print("=" * 60)