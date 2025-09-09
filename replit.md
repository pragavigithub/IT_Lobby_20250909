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
The application now supports reading credentials from a JSON file for better security and configuration management:

### JSON Credential File Format
Location: `/tmp/sap_login/credential.json` (Linux) or `C:/tmp/sap_login/credential.json` (Windows)

```json
{
   "SAP_B1_SERVER": "https://192.168.0.134:50000",
   "SAP_B1_USERNAME": "manager",
   "SAP_B1_PASSWORD": "1422",
   "SAP_B1_COMPANY_DB": "EINV-TESTDB-LIVE-HUST",
   "MYSQL_HOST": "localhost",
   "MYSQL_PORT": "3306",
   "MYSQL_USER": "root",
   "MYSQL_PASSWORD": "root123",
   "MYSQL_DATABASE": "it_lobby",
   "DATABASE_URL": "mysql+pymysql://root:root123@localhost:3306/it_lobby"
}
```

### Fallback Behavior
- If JSON file is not found, application falls back to environment variables
- If MySQL connection fails, application automatically falls back to PostgreSQL (Replit environment)
- All credentials support both JSON and environment variable configuration

## Setup Status
✅ PostgreSQL database configured and connected (migrated from MySQL)
✅ Default admin user created (username: admin, password: admin123)
✅ Environment variables configured (DATABASE_URL, SESSION_SECRET)
✅ Gunicorn server running on port 5000 with webview output
✅ Deployment configuration set for autoscale
✅ All database tables created with default data
✅ Flask application configured for Replit environment with ProxyFix
✅ Application successfully running in Replit environment
✅ GitHub import completed and configured for Replit (September 5, 2025)
✅ Workflow properly configured with webview output type on port 5000

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