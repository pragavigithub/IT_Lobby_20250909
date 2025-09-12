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
   "SAP_B1_SERVER": "https://sap.itlobby.com:50000",
   "SAP_B1_USERNAME": "manager",
   "SAP_B1_PASSWORD": "Ea@12345",
   "SAP_B1_COMPANY_DB": "ZZZ_ITT_TEST_LIVE_DB",
   "MYSQL_HOST": "localhost",
   "MYSQL_PORT": "3306",
   "MYSQL_USER": "root",
   "MYSQL_PASSWORD": "root123",
   "MYSQL_DATABASE": "it_lobby",
   "DATABASE_URL": "mysql+pymysql://root:root123@localhost:3306/it_lobby"
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
✅ GitHub import completed and configured for Replit (September 9, 2025)
✅ Workflow properly configured with webview output type on port 5000
✅ SAP B1 environment variables configured for integration
✅ Application fully operational and accessible via web interface

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
  - Improved user experience with real-time stock validation and seamless item addition
- **Fresh GitHub Import Configuration** (September 11, 2025)
  - Successfully imported GitHub repository and configured for Replit environment
  - All Python dependencies installed from req.txt (46 packages including Flask, gunicorn, SQLAlchemy)
  - PostgreSQL database created and configured successfully
  - Workflow configured with webview output on port 5000
  - Deployment settings configured for autoscale production environment
  - Application fully operational with default admin user (admin/admin123)
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