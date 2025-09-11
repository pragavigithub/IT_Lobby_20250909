-- ========================================================
-- Serial Item Transfer Enhancement Migration
-- This script adds the new columns required for the enhanced
-- Serial Item Transfer workflow with item selection support
-- ========================================================

-- Check if the database is MySQL
-- Use this script for MySQL databases only

-- Add new columns to serial_item_transfer_items table
ALTER TABLE serial_item_transfer_items 
ADD COLUMN is_serial_managed BOOLEAN NOT NULL DEFAULT FALSE 
    COMMENT 'Whether this item requires serial numbers';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN is_batch_managed BOOLEAN NOT NULL DEFAULT FALSE 
    COMMENT 'Whether this item requires batch management';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN item_type VARCHAR(20) NOT NULL DEFAULT 'serial' 
    COMMENT 'Item type: serial or non_serial';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN expected_quantity INT NOT NULL DEFAULT 1 
    COMMENT 'Expected quantity to be scanned/confirmed';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN scanned_quantity INT NOT NULL DEFAULT 0 
    COMMENT 'Actual quantity scanned/confirmed';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN completion_status VARCHAR(20) NOT NULL DEFAULT 'pending' 
    COMMENT 'Completion status: pending, completed, partial';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN parent_item_code VARCHAR(50) NULL 
    COMMENT 'For grouped items (selected item code)';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN line_group_id VARCHAR(50) NULL 
    COMMENT 'Groups related line items together';

-- Make serial_number nullable for non-serial items
ALTER TABLE serial_item_transfer_items 
MODIFY COLUMN serial_number VARCHAR(100) NULL 
    COMMENT 'The entered serial number (nullable for non-serial items)';

-- Update existing records to have proper defaults
UPDATE serial_item_transfer_items 
SET 
    is_serial_managed = TRUE,
    item_type = 'serial',
    expected_quantity = 1,
    scanned_quantity = CASE 
        WHEN serial_number IS NOT NULL THEN 1 
        ELSE 0 
    END,
    completion_status = CASE 
        WHEN serial_number IS NOT NULL THEN 'completed' 
        ELSE 'pending' 
    END
WHERE serial_number IS NOT NULL;

-- Update records without serial numbers (if any exist)
UPDATE serial_item_transfer_items 
SET 
    is_serial_managed = FALSE,
    item_type = 'non_serial',
    expected_quantity = quantity,
    scanned_quantity = quantity,
    completion_status = 'completed'
WHERE serial_number IS NULL;

-- Add indexes for better performance
CREATE INDEX idx_serial_item_transfer_items_is_serial_managed 
ON serial_item_transfer_items(is_serial_managed);

CREATE INDEX idx_serial_item_transfer_items_completion_status 
ON serial_item_transfer_items(completion_status);

CREATE INDEX idx_serial_item_transfer_items_item_type 
ON serial_item_transfer_items(item_type);

-- Print success message
SELECT 'Serial Item Transfer enhancement migration completed successfully!' as message;