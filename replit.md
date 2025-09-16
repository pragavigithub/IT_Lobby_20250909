# WMS (Warehouse Management System) Application

## Overview
This is a Flask-based Warehouse Management System with SAP B1 integration. The application provides inventory management, transfer operations, barcode generation, and invoice creation functionality.

## Project Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL (Replit managed database)
- **Frontend**: HTML templates with Bootstrap styling
- **Integration**: SAP Business One API integration
- **Authentication**: Flask-Login for user management

## Current Configuration
- **Port**: 5000 (configured for Replit webview)
- **Database**: PostgreSQL with automatic table creation
- **Environment**: Production-ready with gunicorn server
- **Logging**: File-based logging system enabled

## Key Features
- User authentication and role management
- Inventory transfer operations
- Barcode and QR code generation
- SAP B1 integration for warehouse operations
- Serial number tracking
- Invoice creation module
- Pick list management
- GRPO (Goods Receipt PO) functionality

## Credential Configuration
The application now uses JSON-based credential management exclusively for better security and configuration management:

### JSON Credential File Format
Location: `C:/tmp/sap_login/credential.json` (Primary) or `/tmp/sap_login/credential.json` (Linux fallback)

```json
{
   "SAP_B1_SERVER": "https://your-sap-server:50000",
   "SAP_B1_USERNAME": "your_username",
   "SAP_B1_PASSWORD": "your_password",
   "SAP_B1_COMPANY_DB": "your_company_db",
   "MYSQL_HOST": "localhost",
   "MYSQL_PORT": "3306",
   "MYSQL_USER": "your_db_user",
   "MYSQL_PASSWORD": "your_db_password",
   "MYSQL_DATABASE": "your_database",
   "DATABASE_URL": "mysql+pymysql://user:password@host:port/database"
}
```

### Credential Loading Behavior
- **Primary Source**: JSON file from `C:/tmp/sap_login/credential.json`
- **Fallback**: Environment variables only if JSON file is not found
- **Database**: MySQL from JSON credentials with PostgreSQL fallback for Replit environment
- **SAP B1 Integration**: All credentials loaded from JSON file, including SAPIntegration class

## Setup Status
✅ PostgreSQL database configured and connected (migrated from MySQL)
✅ Default admin user created (username: admin, password: admin123)
✅ Environment variables configured (DATABASE_URL, SESSION_SECRET)
✅ Gunicorn server running on port 5000 with webview output
✅ Deployment configuration set for autoscale
✅ All database tables created with default data
✅ Flask application configured for Replit environment with ProxyFix
✅ Application successfully running in Replit environment
✅ GitHub import completed and configured for Replit (September 15, 2025)
✅ Workflow properly configured with webview output type on port 5000
✅ SAP B1 environment variables configured for integration
✅ Application fully operational and accessible via web interface
✅ Fresh Replit setup completed with all dependencies installed
✅ **Fresh GitHub Import Setup Completed** (September 16, 2025)
  - Successfully re-imported and configured WMS Flask application from GitHub repository
  - Installed all 46 Python dependencies from pyproject.toml using uv package manager
  - Created and configured PostgreSQL database with automatic environment variable setup
  - Configured workflow with webview output type on port 5000 using gunicorn server
  - Set up deployment configuration for autoscale production environment
  - Application fully operational with proper authentication system (redirects to /login)
  - All database tables created automatically and default branch initialized
  - Environment configured with DATABASE_URL and SESSION_SECRET for production-ready deployment
✅ **Fresh GitHub Import Setup Completed** (September 15, 2025)
  - Successfully imported WMS Flask application from GitHub repository
  - Installed all 46 Python dependencies from pyproject.toml including Flask 3.0.0, gunicorn 21.2.0, SQLAlchemy 2.0.23
  - Created and configured PostgreSQL database with automatic table creation
  - Initialized default admin user (admin/admin123) and branch data (BR001 - Main Branch)
  - Configured workflow with webview output type on port 5000 using gunicorn server
  - Set up deployment configuration for autoscale production environment
  - Application fully operational with authentication system and all modules registered
  - All WMS modules properly configured: GRPO, Inventory Transfer, Invoice Creation, Serial Item Transfer, SO Against Invoice
  - **Replit Environment Setup Verified** (September 15, 2025):
    - PostgreSQL database successfully provisioned and connected
    - All 46 Python dependencies installed and available via pyproject.toml
    - Flask application running on port 5000 with webview output and ProxyFix middleware
    - All database tables created automatically on startup
    - Default branch (BR001) and system initialized
    - All 5 WMS modules properly registered and accessible
    - Environment variables (DATABASE_URL, SESSION_SECRET) configured automatically
    - Application responding correctly with 302 redirects to authentication system

## Default Credentials
- **Username**: admin
- **Password**: admin123
- **Role**: System Administrator

## Modules
- Main application routes
- Inventory transfer module
- Serial item transfer module
- Invoice creation module
- SAP B1 integration utilities
- Barcode generation utilities

## Recent Changes
- **Serial Item Transfer Module Improvements** (September 12, 2025)
  - Fixed line item removal issue by eliminating duplicate JavaScript functions with conflicting URLs
  - Implemented non-serial item handling with auto-populate quantity 1 and manual modification capability
  - Added quantity validation to restrict entries to available stock or less
  - Enhanced serial number entry behavior to auto-populate line items and disable input when quantity matches
  - **CRITICAL FIX**: Resolved JavaScript syntax errors preventing ItemCode dropdown from loading
  - Added mock data for offline SAP B1 mode with 5 sample items for testing
  - Consolidated JavaScript code to eliminate duplicates and syntax errors
  - **NON-SERIAL ITEM FIXES**: Fixed quantity auto-population timing issues and modified backend to create separate line items instead of consolidating quantities
  - **QUANTITY DISPLAY FIXES**: Fixed all template displays to show total quantities instead of line item counts throughout the application (detail pages, dashboard, approval screens)
  - **SAP B1 QUANTITY POSTING FIX**: Fixed critical issue where non-serial items were posting quantity 1 to SAP B1 instead of actual entered quantity (e.g., quantity 5)
  - **SAP B1 JSON SERIALNUMBERS ARRAY**: Modified non-serial items to have empty SerialNumbers array instead of placeholder entries for cleaner SAP B1 integration
  - **SAP B1 DOCNUM DISPLAY**: Added SAP B1 document number display to both detail and index screens after successful posting
  - Improved user experience with real-time stock validation and seamless item addition
- **SO Against Invoice Template Mapping Fix** (September 15, 2025)
  - Fixed critical template mapping issue where module was looking for 'so_against_invoice/index.html' but templates were stored directly in templates/
  - Updated all render_template calls to use direct template names: 'index.html', 'create.html', 'detail.html'
  - Added template_folder='templates' parameter to blueprint declaration for proper template resolution
  - Module now fully functional with all endpoints working correctly
  - Verified all MySQL migration files are up-to-date with SO Against Invoice models
- **Fresh GitHub Import Configuration** (September 11, 2025)
  - Successfully imported GitHub repository and configured for Replit environment
  - All Python dependencies installed from req.txt (46 packages including Flask, gunicorn, SQLAlchemy)
  - PostgreSQL database created and configured successfully
  - Workflow configured with webview output on port 5000
  - Deployment settings configured for autoscale production environment
  - Application fully operational with default admin user (admin/admin123)
- **Module Registration Fix** (September 15, 2025)
  - Fixed critical routing issue where serial_item_transfer blueprint was not registered
  - Added missing blueprint import and registration in main_controller.py
  - Updated template searchpath to include serial_item_transfer templates
  - So_against_Invoice module confirmed fully operational and up-to-date
  - MySQL migration files verified as comprehensive and current
  - All modules now properly registered and accessible via navigation
- **Updated JSON Credential System** (September 9, 2025)
  - Updated SAP B1 credentials to use sap.itlobby.com server
  - Modified SAPIntegration class to read credentials exclusively from JSON file
  - Primary credential path: `C:/tmp/sap_login/credential.json`
  - All SAP B1 and MySQL credentials now loaded from JSON file
- **JSON Credential Loading System** (September 5, 2025)
  - Added support for reading SAP B1 and MySQL credentials from JSON file
  - Default credential path: `/tmp/sap_login/credential.json` (Linux) or `C:/tmp/sap_login/credential.json` (Windows)
  - Automatic fallback to environment variables if JSON file not found
  - MySQL connection with PostgreSQL fallback for Replit environment
- Migrated from MySQL to PostgreSQL for Replit environment (September 5, 2025)
- Database configuration updated to use Replit's managed PostgreSQL
- Workflow configured with webview output on port 5000
- ProxyFix middleware properly configured for Replit iframe environment
- Deployment configuration set for autoscale production deployment
- PostgreSQL-specific constraint handling implemented
- Default branch and admin user initialized successfully