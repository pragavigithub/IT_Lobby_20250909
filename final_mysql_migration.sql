-- ========================================================================
-- FINAL MYSQL MIGRATION - Serial Item Transfer Enhancement
-- This single file contains all database changes needed to fix the schema
-- ========================================================================

-- Use the correct database
USE it_lobby;

-- Check current database
SELECT DATABASE() as current_database;

-- ========================================================================
-- STEP 1: Add missing columns to serial_item_transfer_items table
-- ========================================================================

-- Add is_serial_managed column
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS is_serial_managed BOOLEAN NOT NULL DEFAULT FALSE 
COMMENT 'Whether this item requires serial numbers';

-- Add is_batch_managed column  
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS is_batch_managed BOOLEAN NOT NULL DEFAULT FALSE 
COMMENT 'Whether this item requires batch management';

-- Add item_type column
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS item_type VARCHAR(20) NOT NULL DEFAULT 'serial' 
COMMENT 'Item type: serial or non_serial';

-- Add expected_quantity column
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS expected_quantity INT NOT NULL DEFAULT 1 
COMMENT 'Expected quantity to be scanned/confirmed';

-- Add scanned_quantity column
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS scanned_quantity INT NOT NULL DEFAULT 0 
COMMENT 'Actual quantity scanned/confirmed';

-- Add completion_status column
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS completion_status VARCHAR(20) NOT NULL DEFAULT 'pending' 
COMMENT 'Completion status: pending, completed, partial';

-- Add parent_item_code column
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS parent_item_code VARCHAR(50) NULL 
COMMENT 'For grouped items (selected item code)';

-- Add line_group_id column
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS line_group_id VARCHAR(50) NULL 
COMMENT 'Groups related line items together';

-- ========================================================================
-- STEP 2: Modify existing columns
-- ========================================================================

-- Make serial_number nullable for non-serial items
ALTER TABLE serial_item_transfer_items 
MODIFY COLUMN serial_number VARCHAR(100) NULL 
COMMENT 'The entered serial number (nullable for non-serial items)';

-- ========================================================================
-- STEP 3: Update existing data with proper defaults
-- ========================================================================

-- Update records that have serial numbers (serial items)
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
WHERE serial_number IS NOT NULL AND serial_number != '';

-- Update records without serial numbers (non-serial items)
UPDATE serial_item_transfer_items 
SET 
    is_serial_managed = FALSE,
    item_type = 'non_serial',
    expected_quantity = COALESCE(quantity, 1),
    scanned_quantity = COALESCE(quantity, 1),
    completion_status = 'completed'
WHERE serial_number IS NULL OR serial_number = '';

-- ========================================================================
-- STEP 4: Create performance indexes
-- ========================================================================

-- Create index for is_serial_managed (if not exists)
CREATE INDEX IF NOT EXISTS idx_serial_item_transfer_items_is_serial_managed 
ON serial_item_transfer_items(is_serial_managed);

-- Create index for completion_status (if not exists)
CREATE INDEX IF NOT EXISTS idx_serial_item_transfer_items_completion_status 
ON serial_item_transfer_items(completion_status);

-- Create index for item_type (if not exists)
CREATE INDEX IF NOT EXISTS idx_serial_item_transfer_items_item_type 
ON serial_item_transfer_items(item_type);

-- Create index for parent_item_code (if not exists)
CREATE INDEX IF NOT EXISTS idx_serial_item_transfer_items_parent_item_code 
ON serial_item_transfer_items(parent_item_code);

-- ========================================================================
-- STEP 5: Verification and final checks
-- ========================================================================

-- Show table structure to verify changes
DESCRIBE serial_item_transfer_items;

-- Count total records
SELECT COUNT(*) as total_records FROM serial_item_transfer_items;

-- Show breakdown by item type
SELECT 
    item_type,
    is_serial_managed,
    completion_status,
    COUNT(*) as count
FROM serial_item_transfer_items 
GROUP BY item_type, is_serial_managed, completion_status
ORDER BY item_type, is_serial_managed;

-- ========================================================================
-- SUCCESS MESSAGE
-- ========================================================================

SELECT 
    '✅ Serial Item Transfer Enhancement Migration Completed Successfully!' as message,
    NOW() as migration_timestamp,
    DATABASE() as database_name;

-- ========================================================================
-- MIGRATION COMPLETE
-- ========================================================================