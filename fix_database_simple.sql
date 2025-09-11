-- Quick fix for Serial Item Transfer Enhancement
-- Run this SQL script in your MySQL database

USE it_lobby;

-- Add missing columns to serial_item_transfer_items table
ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS is_serial_managed BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS is_batch_managed BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS item_type VARCHAR(20) NOT NULL DEFAULT 'serial';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS expected_quantity INT NOT NULL DEFAULT 1;

ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS scanned_quantity INT NOT NULL DEFAULT 0;

ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS completion_status VARCHAR(20) NOT NULL DEFAULT 'pending';

ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS parent_item_code VARCHAR(50) NULL;

ALTER TABLE serial_item_transfer_items 
ADD COLUMN IF NOT EXISTS line_group_id VARCHAR(50) NULL;

-- Make serial_number nullable for non-serial items
ALTER TABLE serial_item_transfer_items 
MODIFY COLUMN serial_number VARCHAR(100) NULL;

-- Update existing records with proper defaults
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

-- Update records without serial numbers
UPDATE serial_item_transfer_items 
SET 
    is_serial_managed = FALSE,
    item_type = 'non_serial',
    expected_quantity = COALESCE(quantity, 1),
    scanned_quantity = COALESCE(quantity, 1),
    completion_status = 'completed'
WHERE serial_number IS NULL OR serial_number = '';

SELECT 'Migration completed successfully!' as message;