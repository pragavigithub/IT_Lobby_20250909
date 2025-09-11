#!/usr/bin/env python3
"""
========================================================================
CONSOLIDATED MYSQL MIGRATION - Serial Item Transfer Enhancement
This single Python file fixes the database schema for the enhanced
Serial Item Transfer workflow with item selection support.
========================================================================
"""

import json
import os
import sys
import logging
import pymysql
from datetime import datetime

class MySQLMigration:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for migration"""
        # Create formatters
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Create console handler with UTF-8 encoding
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Create file handler with UTF-8 encoding
        file_handler = logging.FileHandler('mysql_migration.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def load_credentials(self):
        """Load credentials from JSON file"""
        file_paths = ["C:/tmp/sap_login/credential.json", "/tmp/sap_login/credential.json"]
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        credentials = json.load(f)
                    self.logger.info(f"[SUCCESS] Credentials loaded from {file_path}")
                    return credentials
            except Exception as e:
                self.logger.warning(f"[WARNING] Could not load credentials from {file_path}: {e}")
                continue
        
        self.logger.error("[ERROR] No credential file found")
        return {}

    def connect_database(self):
        """Connect to MySQL database"""
        try:
            creds = self.load_credentials()
            
            self.connection = pymysql.connect(
                host=creds.get('MYSQL_HOST', 'localhost'),
                port=int(creds.get('MYSQL_PORT', 3306)),
                user=creds.get('MYSQL_USER', 'root'),
                password=creds.get('MYSQL_PASSWORD', ''),
                database=creds.get('MYSQL_DATABASE', 'it_lobby'),
                charset='utf8mb4',
                autocommit=False
            )
            
            self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            self.logger.info("[SUCCESS] Connected to MySQL database successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to connect to database: {e}")
            return False

    def check_column_exists(self, table_name, column_name):
        """Check if a column exists in the table"""
        try:
            query = """
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = %s 
            AND COLUMN_NAME = %s
            """
            self.cursor.execute(query, (table_name, column_name))
            result = self.cursor.fetchone()
            return result['count'] > 0
        except Exception as e:
            self.logger.error(f"[ERROR] Error checking column {column_name}: {e}")
            return False

    def add_missing_columns(self):
        """Add all missing columns to serial_item_transfer_items table"""
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
        
        self.logger.info(f"[INFO] Checking table: {table_name}")
        
        # Check which columns need to be added
        columns_needed = []
        for column_name, column_def in columns_to_add:
            if not self.check_column_exists(table_name, column_name):
                columns_needed.append((column_name, column_def))
                self.logger.info(f"  [NEEDED] Column '{column_name}' needs to be added")
            else:
                self.logger.info(f"  [EXISTS] Column '{column_name}' already exists")
        
        if not columns_needed:
            self.logger.info("[SUCCESS] All required columns already exist!")
            return True
        
        # Add missing columns
        self.logger.info(f"[PROGRESS] Adding {len(columns_needed)} missing columns...")
        
        for column_name, column_def in columns_needed:
            try:
                alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
                self.logger.info(f"  [ADDING] Adding column: {column_name}")
                self.cursor.execute(alter_query)
                self.logger.info(f"  [SUCCESS] Successfully added column: {column_name}")
            except Exception as e:
                self.logger.error(f"  [ERROR] Failed to add column {column_name}: {e}")
                return False
        
        return True

    def make_serial_number_nullable(self):
        """Make serial_number column nullable for non-serial items"""
        try:
            self.logger.info("[MODIFY] Making serial_number column nullable...")
            self.cursor.execute("ALTER TABLE serial_item_transfer_items MODIFY COLUMN serial_number VARCHAR(100) NULL")
            self.logger.info("[SUCCESS] Successfully made serial_number nullable")
            return True
        except Exception as e:
            self.logger.warning(f"[WARNING] Could not modify serial_number column: {e}")
            return True  # Non-critical error

    def update_existing_data(self):
        """Update existing records with proper defaults"""
        try:
            self.logger.info("[UPDATE] Updating existing records with proper defaults...")
            
            # Update records with serial numbers
            query1 = """
                UPDATE serial_item_transfer_items 
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
            """
            self.cursor.execute(query1)
            serial_records = self.cursor.rowcount
            self.logger.info(f"  [SUCCESS] Updated {serial_records} serial item records")
            
            # Update records without serial numbers
            query2 = """
                UPDATE serial_item_transfer_items 
                SET 
                    is_serial_managed = FALSE,
                    item_type = 'non_serial',
                    expected_quantity = COALESCE(quantity, 1),
                    scanned_quantity = COALESCE(quantity, 1),
                    completion_status = 'completed'
                WHERE serial_number IS NULL OR serial_number = ''
            """
            self.cursor.execute(query2)
            non_serial_records = self.cursor.rowcount
            self.logger.info(f"  [SUCCESS] Updated {non_serial_records} non-serial item records")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to update existing data: {e}")
            return False

    def create_indexes(self):
        """Create performance indexes"""
        self.logger.info("[INDEXES] Creating performance indexes...")
        indexes = [
            "CREATE INDEX idx_serial_items_is_serial_managed ON serial_item_transfer_items(is_serial_managed)",
            "CREATE INDEX idx_serial_items_completion_status ON serial_item_transfer_items(completion_status)",
            "CREATE INDEX idx_serial_items_item_type ON serial_item_transfer_items(item_type)",
            "CREATE INDEX idx_serial_items_parent_item_code ON serial_item_transfer_items(parent_item_code)"
        ]
        
        success_count = 0
        for index_query in indexes:
            try:
                self.cursor.execute(index_query)
                success_count += 1
                self.logger.info(f"  [SUCCESS] Created index successfully")
            except Exception as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    success_count += 1
                    self.logger.info(f"  [EXISTS] Index already exists (skipping)")
                else:
                    self.logger.warning(f"  [WARNING] Could not create index: {e}")
        
        self.logger.info(f"[COMPLETE] {success_count}/{len(indexes)} indexes ready")
        return True

    def verify_migration(self):
        """Verify migration was successful"""
        try:
            self.logger.info("[VERIFY] Verifying migration...")
            
            # Check table structure
            self.cursor.execute("DESCRIBE serial_item_transfer_items")
            columns = self.cursor.fetchall()
            column_names = [col['Field'] for col in columns]
            
            required_columns = [
                'is_serial_managed', 'is_batch_managed', 'item_type', 
                'expected_quantity', 'scanned_quantity', 'completion_status',
                'parent_item_code', 'line_group_id'
            ]
            
            missing_columns = [col for col in required_columns if col not in column_names]
            if missing_columns:
                self.logger.error(f"[ERROR] Missing columns after migration: {missing_columns}")
                return False
            
            # Count records
            self.cursor.execute("SELECT COUNT(*) as count FROM serial_item_transfer_items")
            record_count = self.cursor.fetchone()['count']
            self.logger.info(f"[INFO] Table has {record_count} records")
            
            # Show breakdown
            self.cursor.execute("""
                SELECT 
                    item_type,
                    is_serial_managed,
                    completion_status,
                    COUNT(*) as count
                FROM serial_item_transfer_items 
                GROUP BY item_type, is_serial_managed, completion_status
                ORDER BY item_type, is_serial_managed
            """)
            breakdown = self.cursor.fetchall()
            
            if breakdown:
                self.logger.info("[BREAKDOWN] Record breakdown:")
                for row in breakdown:
                    self.logger.info(f"  - {row['item_type']} (serial_managed: {row['is_serial_managed']}, status: {row['completion_status']}): {row['count']} records")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Verification failed: {e}")
            return False

    def run_migration(self):
        """Run the complete migration process"""
        print("=" * 80)
        print("CONSOLIDATED MYSQL MIGRATION - Serial Item Transfer Enhancement")
        print("=" * 80)
        print()
        
        self.logger.info("[START] Starting Serial Item Transfer Enhancement Migration")
        
        # Connect to database
        if not self.connect_database():
            self.logger.error("Cannot proceed without database connection")
            return False
        
        try:
            # Step 1: Add missing columns
            if not self.add_missing_columns():
                self.logger.error("Failed to add missing columns")
                return False
            
            # Step 2: Make serial_number nullable
            if not self.make_serial_number_nullable():
                self.logger.error("Failed to modify serial_number column")
                return False
            
            # Step 3: Update existing data
            if not self.update_existing_data():
                self.logger.error("Failed to update existing data")
                return False
            
            # Step 4: Create indexes
            if not self.create_indexes():
                self.logger.error("Failed to create indexes")
                return False
            
            # Step 5: Commit changes
            self.connection.commit()
            self.logger.info("[COMMIT] Committed all changes to database")
            
            # Step 6: Verify migration
            if not self.verify_migration():
                self.logger.error("Migration verification failed")
                return False
            
            self.logger.info("[COMPLETE] Migration completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Migration failed: {e}")
            self.connection.rollback()
            self.logger.info("[ROLLBACK] Rolled back all changes")
            return False
            
        finally:
            if self.connection:
                self.connection.close()
                self.logger.info("[CLOSED] Database connection closed")

    def close(self):
        """Clean up database connections"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

def main():
    """Main function to run the migration"""
    migration = MySQLMigration()
    
    try:
        success = migration.run_migration()
        
        print()
        print("=" * 80)
        if success:
            print("[SUCCESS] MIGRATION COMPLETED SUCCESSFULLY!")
            print("Your database schema has been updated.")
            print("You can now restart your application and the error should be resolved.")
        else:
            print("[FAILED] MIGRATION FAILED!")
            print("Please check the mysql_migration.log file for details.")
        print("=" * 80)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Migration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return 1
    finally:
        migration.close()

if __name__ == "__main__":
    sys.exit(main())