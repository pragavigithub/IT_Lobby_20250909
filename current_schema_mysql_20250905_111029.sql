-- WMS Database Schema - Generated on 2025-09-05 11:10:29
-- Models: User, GRPODocument, GRPOItem, InventoryTransfer, InventoryTransferItem, PickList, PickListItem, PickListLine, PickListBinAllocation, InventoryCount, InventoryCountItem, BarcodeLabel, BinLocation, BinItem, BinScanningLog, QRCodeLabel, SalesOrder, SalesOrderLine, DocumentNumberSeries, SerialNumberTransfer, SerialNumberTransferItem, SerialNumberTransferSerial, SerialItemTransfer, SerialItemTransferItem, Branch, UserSession, PasswordResetToken, PurchaseDeliveryNote, InvoiceDocument, InvoiceLine, InvoiceSerialNumber, SerialNumberLookup, Warehouse, BusinessPartner

-- Table: users (Model: User)
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(255),
  `email` VARCHAR(255),
  `password_hash` VARCHAR(255),
  `first_name` VARCHAR(255),
  `last_name` VARCHAR(255),
  `role` VARCHAR(255),
  `branch_id` VARCHAR(255),
  `branch_name` VARCHAR(255),
  `default_branch_id` VARCHAR(255),
  `active` BOOLEAN DEFAULT TRUE,
  `must_change_password` BOOLEAN DEFAULT FALSE,
  `last_login` DATETIME,
  `permissions` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: grpo_documents (Model: GRPODocument)
CREATE TABLE IF NOT EXISTS `grpo_documents` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `po_number` VARCHAR(255),
  `supplier_code` VARCHAR(255),
  `supplier_name` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `user_id` INT,
  `qc_approver_id` INT,
  `qc_approved_at` DATETIME,
  `qc_notes` TEXT,
  `status` VARCHAR(255),
  `po_total` DECIMAL,
  `sap_document_number` VARCHAR(255),
  `notes` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: grpo_items (Model: GRPOItem)
CREATE TABLE IF NOT EXISTS `grpo_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `grpo_id` INT,
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `quantity` DECIMAL,
  `received_quantity` DECIMAL,
  `unit_price` DECIMAL,
  `line_total` DECIMAL,
  `unit_of_measure` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `bin_location` VARCHAR(255),
  `batch_number` VARCHAR(255),
  `serial_number` VARCHAR(255),
  `expiry_date` DATE,
  `barcode` VARCHAR(255),
  `qc_status` VARCHAR(255),
  `po_line_number` INT,
  `base_entry` INT,
  `base_line` INT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: inventory_transfers (Model: InventoryTransfer)
CREATE TABLE IF NOT EXISTS `inventory_transfers` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `transfer_request_number` VARCHAR(255),
  `sap_document_number` VARCHAR(255),
  `status` VARCHAR(255),
  `user_id` INT,
  `qc_approver_id` INT,
  `qc_approved_at` DATETIME,
  `qc_notes` TEXT,
  `from_warehouse` VARCHAR(255),
  `to_warehouse` VARCHAR(255),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: inventory_transfer_items (Model: InventoryTransferItem)
CREATE TABLE IF NOT EXISTS `inventory_transfer_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `inventory_transfer_id` INT,
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `quantity` FLOAT NOT NULL,
  `requested_quantity` FLOAT NOT NULL,
  `transferred_quantity` FLOAT,
  `remaining_quantity` FLOAT NOT NULL,
  `unit_of_measure` VARCHAR(255),
  `from_bin` VARCHAR(255),
  `to_bin` VARCHAR(255),
  `from_bin_location` VARCHAR(255),
  `to_bin_location` VARCHAR(255),
  `batch_number` VARCHAR(255),
  `available_batches` TEXT,
  `qc_status` VARCHAR(255),
  `qc_notes` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: pick_lists (Model: PickList)
CREATE TABLE IF NOT EXISTS `pick_lists` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `absolute_entry` INT,
  `name` VARCHAR(255),
  `owner_code` INT,
  `owner_name` VARCHAR(255),
  `pick_date` DATETIME,
  `remarks` TEXT,
  `status` VARCHAR(255),
  `object_type` VARCHAR(255),
  `use_base_units` VARCHAR(255),
  `sales_order_number` VARCHAR(255),
  `pick_list_number` VARCHAR(255),
  `user_id` INT,
  `approver_id` INT,
  `priority` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `customer_code` VARCHAR(255),
  `customer_name` VARCHAR(255),
  `total_items` INT,
  `picked_items` INT,
  `notes` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: pick_list_items (Model: PickListItem)
CREATE TABLE IF NOT EXISTS `pick_list_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `pick_list_id` INT,
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `quantity` FLOAT NOT NULL,
  `picked_quantity` FLOAT,
  `unit_of_measure` VARCHAR(255),
  `bin_location` VARCHAR(255),
  `batch_number` VARCHAR(255),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: pick_list_lines (Model: PickListLine)
CREATE TABLE IF NOT EXISTS `pick_list_lines` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `pick_list_id` INT,
  `absolute_entry` INT,
  `line_number` INT NOT NULL,
  `order_entry` INT,
  `order_row_id` INT,
  `picked_quantity` FLOAT,
  `pick_status` VARCHAR(255),
  `released_quantity` FLOAT,
  `previously_released_quantity` FLOAT,
  `base_object_type` INT,
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `unit_of_measure` VARCHAR(255),
  `serial_numbers` TEXT,
  `batch_numbers` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: pick_list_bin_allocations (Model: PickListBinAllocation)
CREATE TABLE IF NOT EXISTS `pick_list_bin_allocations` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `pick_list_line_id` INT,
  `bin_abs_entry` INT,
  `quantity` FLOAT NOT NULL,
  `allow_negative_quantity` VARCHAR(255),
  `serial_and_batch_numbers_base_line` INT,
  `base_line_number` INT,
  `bin_code` VARCHAR(255),
  `bin_location` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `picked_quantity` FLOAT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: inventory_counts (Model: InventoryCount)
CREATE TABLE IF NOT EXISTS `inventory_counts` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `count_number` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `bin_location` VARCHAR(255),
  `status` VARCHAR(255),
  `user_id` INT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: inventory_count_items (Model: InventoryCountItem)
CREATE TABLE IF NOT EXISTS `inventory_count_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `inventory_count_id` INT,
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `system_quantity` FLOAT NOT NULL,
  `counted_quantity` FLOAT NOT NULL,
  `variance` FLOAT NOT NULL,
  `unit_of_measure` VARCHAR(255),
  `batch_number` VARCHAR(255),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: barcode_labels (Model: BarcodeLabel)
CREATE TABLE IF NOT EXISTS `barcode_labels` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `item_code` VARCHAR(255),
  `barcode` VARCHAR(255),
  `label_format` VARCHAR(255),
  `print_count` INT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `last_printed` DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: bin_locations (Model: BinLocation)
CREATE TABLE IF NOT EXISTS `bin_locations` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `warehouse_code` VARCHAR(255),
  `bin_code` VARCHAR(255),
  `bin_name` VARCHAR(255),
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: bin_items (Model: BinItem)
CREATE TABLE IF NOT EXISTS `bin_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `bin_code` VARCHAR(255),
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `batch_number` VARCHAR(255),
  `quantity` FLOAT,
  `available_quantity` FLOAT,
  `committed_quantity` FLOAT,
  `uom` VARCHAR(255),
  `expiry_date` DATE,
  `manufacturing_date` DATE,
  `admission_date` DATE,
  `warehouse_code` VARCHAR(255),
  `sap_abs_entry` INT,
  `sap_system_number` INT,
  `sap_doc_entry` INT,
  `batch_attribute1` VARCHAR(255),
  `batch_attribute2` VARCHAR(255),
  `batch_status` VARCHAR(255),
  `last_sap_sync` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: bin_scanning_logs (Model: BinScanningLog)
CREATE TABLE IF NOT EXISTS `bin_scanning_logs` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `bin_code` VARCHAR(255),
  `user_id` INT,
  `scan_type` VARCHAR(255),
  `scan_data` TEXT,
  `items_found` INT,
  `scan_timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: qr_code_labels (Model: QRCodeLabel)
CREATE TABLE IF NOT EXISTS `qr_code_labels` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `label_type` VARCHAR(255),
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `po_number` VARCHAR(255),
  `batch_number` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `bin_code` VARCHAR(255),
  `quantity` DECIMAL,
  `uom` VARCHAR(255),
  `expiry_date` DATE,
  `qr_content` TEXT NOT NULL,
  `qr_format` VARCHAR(255),
  `grpo_item_id` INT,
  `inventory_transfer_item_id` INT,
  `user_id` INT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: sales_orders (Model: SalesOrder)
CREATE TABLE IF NOT EXISTS `sales_orders` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `doc_entry` INT NOT NULL UNIQUE,
  `doc_num` INT,
  `doc_type` VARCHAR(255),
  `doc_date` DATETIME,
  `doc_due_date` DATETIME,
  `card_code` VARCHAR(255),
  `card_name` VARCHAR(255),
  `address` TEXT,
  `doc_total` FLOAT,
  `doc_currency` VARCHAR(255),
  `comments` TEXT,
  `document_status` VARCHAR(255),
  `last_sap_sync` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: sales_order_lines (Model: SalesOrderLine)
CREATE TABLE IF NOT EXISTS `sales_order_lines` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `sales_order_id` INT,
  `line_num` INT NOT NULL,
  `item_code` VARCHAR(255),
  `item_description` VARCHAR(255),
  `quantity` FLOAT,
  `open_quantity` FLOAT,
  `delivered_quantity` FLOAT,
  `unit_price` FLOAT,
  `line_total` FLOAT,
  `warehouse_code` VARCHAR(255),
  `unit_of_measure` VARCHAR(255),
  `line_status` VARCHAR(255),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: document_number_series (Model: DocumentNumberSeries)
CREATE TABLE IF NOT EXISTS `document_number_series` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `document_type` VARCHAR(255),
  `prefix` VARCHAR(255),
  `current_number` INT,
  `year_suffix` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: serial_number_transfers (Model: SerialNumberTransfer)
CREATE TABLE IF NOT EXISTS `serial_number_transfers` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `transfer_number` VARCHAR(255),
  `sap_document_number` VARCHAR(255),
  `status` VARCHAR(255),
  `user_id` INT,
  `qc_approver_id` INT,
  `qc_approved_at` DATETIME,
  `qc_notes` TEXT,
  `from_warehouse` VARCHAR(255),
  `to_warehouse` VARCHAR(255),
  `priority` VARCHAR(255),
  `notes` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: serial_number_transfer_items (Model: SerialNumberTransferItem)
CREATE TABLE IF NOT EXISTS `serial_number_transfer_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `serial_transfer_id` INT,
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `quantity` INT NOT NULL,
  `unit_of_measure` VARCHAR(255),
  `from_warehouse_code` VARCHAR(255),
  `to_warehouse_code` VARCHAR(255),
  `qc_status` VARCHAR(255),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: serial_number_transfer_serials (Model: SerialNumberTransferSerial)
CREATE TABLE IF NOT EXISTS `serial_number_transfer_serials` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `transfer_item_id` INT,
  `serial_number` VARCHAR(255),
  `internal_serial_number` VARCHAR(255),
  `system_serial_number` INT,
  `is_validated` BOOLEAN DEFAULT FALSE,
  `validation_error` TEXT,
  `manufacturing_date` DATE,
  `expiry_date` DATE,
  `admission_date` DATE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: serial_item_transfers (Model: SerialItemTransfer)
CREATE TABLE IF NOT EXISTS `serial_item_transfers` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `transfer_number` VARCHAR(255),
  `sap_document_number` VARCHAR(255),
  `status` VARCHAR(255),
  `user_id` INT,
  `qc_approver_id` INT,
  `qc_approved_at` DATETIME,
  `qc_notes` TEXT,
  `from_warehouse` VARCHAR(255),
  `to_warehouse` VARCHAR(255),
  `priority` VARCHAR(255),
  `notes` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: serial_item_transfer_items (Model: SerialItemTransferItem)
CREATE TABLE IF NOT EXISTS `serial_item_transfer_items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `serial_item_transfer_id` INT,
  `serial_number` VARCHAR(255),
  `item_code` VARCHAR(255),
  `item_description` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `quantity` INT NOT NULL,
  `unit_of_measure` VARCHAR(255),
  `from_warehouse_code` VARCHAR(255),
  `to_warehouse_code` VARCHAR(255),
  `qc_status` VARCHAR(255),
  `validation_status` VARCHAR(255),
  `validation_error` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: branches (Model: Branch)
CREATE TABLE IF NOT EXISTS `branches` (
  `id` VARCHAR(255),
  `name` VARCHAR(255),
  `description` VARCHAR(255),
  `branch_code` VARCHAR(255),
  `branch_name` VARCHAR(255),
  `address` VARCHAR(255),
  `city` VARCHAR(255),
  `state` VARCHAR(255),
  `postal_code` VARCHAR(255),
  `country` VARCHAR(255),
  `phone` VARCHAR(255),
  `email` VARCHAR(255),
  `manager_name` VARCHAR(255),
  `warehouse_codes` TEXT,
  `active` BOOLEAN DEFAULT TRUE,
  `is_default` BOOLEAN DEFAULT FALSE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: user_sessions (Model: UserSession)
CREATE TABLE IF NOT EXISTS `user_sessions` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT,
  `session_token` VARCHAR(255),
  `branch_id` VARCHAR(255),
  `login_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `logout_time` DATETIME,
  `ip_address` VARCHAR(255),
  `user_agent` TEXT,
  `active` BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: password_reset_tokens (Model: PasswordResetToken)
CREATE TABLE IF NOT EXISTS `password_reset_tokens` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT,
  `token` VARCHAR(255),
  `expires_at` DATETIME NOT NULL,
  `used` BOOLEAN DEFAULT FALSE,
  `created_by` INT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: purchase_delivery_notes (Model: PurchaseDeliveryNote)
CREATE TABLE IF NOT EXISTS `purchase_delivery_notes` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `grpo_id` INT,
  `external_reference` VARCHAR(255),
  `sap_document_number` VARCHAR(255),
  `supplier_code` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `document_date` DATE,
  `due_date` DATE,
  `total_amount` DECIMAL,
  `status` VARCHAR(255),
  `json_payload` TEXT,
  `sap_response` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `posted_at` DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: invoice_documents (Model: InvoiceDocument)
CREATE TABLE IF NOT EXISTS `invoice_documents` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `invoice_number` VARCHAR(255),
  `customer_code` VARCHAR(255),
  `customer_name` VARCHAR(255),
  `branch_id` INT,
  `branch_name` VARCHAR(255),
  `user_id` INT,
  `status` VARCHAR(255),
  `bpl_id` INT,
  `bpl_name` VARCHAR(255),
  `doc_date` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `due_date` DATETIME,
  `total_amount` DECIMAL,
  `sap_doc_entry` INT,
  `sap_doc_num` VARCHAR(255),
  `notes` TEXT,
  `json_payload` TEXT,
  `sap_response` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: invoice_lines (Model: InvoiceLine)
CREATE TABLE IF NOT EXISTS `invoice_lines` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `invoice_id` INT,
  `line_number` INT NOT NULL,
  `item_code` VARCHAR(255),
  `item_description` VARCHAR(255),
  `quantity` DECIMAL,
  `unit_price` DECIMAL,
  `line_total` DECIMAL,
  `warehouse_code` VARCHAR(255),
  `warehouse_name` VARCHAR(255),
  `tax_code` VARCHAR(255),
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: invoice_serial_numbers (Model: InvoiceSerialNumber)
CREATE TABLE IF NOT EXISTS `invoice_serial_numbers` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `invoice_line_id` INT,
  `serial_number` VARCHAR(255),
  `item_code` VARCHAR(255),
  `item_description` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `customer_code` VARCHAR(255),
  `customer_name` VARCHAR(255),
  `bpl_id` INT,
  `bpl_name` VARCHAR(255),
  `base_line_number` INT,
  `quantity` DECIMAL,
  `validation_status` VARCHAR(255),
  `validation_error` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: serial_number_lookups (Model: SerialNumberLookup)
CREATE TABLE IF NOT EXISTS `serial_number_lookups` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `serial_number` VARCHAR(255),
  `item_code` VARCHAR(255),
  `item_name` VARCHAR(255),
  `warehouse_code` VARCHAR(255),
  `warehouse_name` VARCHAR(255),
  `branch_id` INT,
  `branch_name` VARCHAR(255),
  `lookup_status` VARCHAR(255),
  `lookup_error` TEXT,
  `sap_response` TEXT,
  `last_updated` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: warehouses (Model: Warehouse)
CREATE TABLE IF NOT EXISTS `warehouses` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `warehouse_code` VARCHAR(255),
  `warehouse_name` VARCHAR(255),
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- Table: business_partners (Model: BusinessPartner)
CREATE TABLE IF NOT EXISTS `business_partners` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `card_code` VARCHAR(255),
  `card_name` VARCHAR(255),
  `card_type` VARCHAR(255),
  `is_active` BOOLEAN DEFAULT TRUE,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

