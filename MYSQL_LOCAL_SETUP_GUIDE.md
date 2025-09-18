# MySQL Local Machine Setup Guide

## Issue: Login Not Working with Local MySQL Integration

### Root Cause
The application expects credentials to be loaded from a JSON file first, then falls back to environment variables. If the JSON credential file doesn't exist or doesn't contain the correct MySQL credentials, the application may not connect properly to your local MySQL database.

### Solution

#### Step 1: Create the Credential JSON File

Create a file at one of these locations:
- **Windows**: `C:/tmp/sap_login/credential.json`
- **Linux/Mac**: `/tmp/sap_login/credential.json`

#### Step 2: Add Your MySQL Credentials

Put the following JSON content in the file, replacing the values with your actual MySQL settings:

```json
{
   "SAP_B1_SERVER": "https://your-sap-server:50000",
   "SAP_B1_USERNAME": "your_sap_username",
   "SAP_B1_PASSWORD": "your_sap_password",
   "SAP_B1_COMPANY_DB": "your_company_database",
   "MYSQL_HOST": "localhost",
   "MYSQL_PORT": "3306",
   "MYSQL_USER": "your_mysql_username",
   "MYSQL_PASSWORD": "your_mysql_password",
   "MYSQL_DATABASE": "your_wms_database",
   "DATABASE_URL": "mysql+pymysql://your_mysql_username:your_mysql_password@localhost:3306/your_wms_database"
}
```

#### Step 3: Create the Directory Structure

Make sure the directory exists:

**Windows:**
```cmd
mkdir C:\tmp\sap_login
```

**Linux/Mac:**
```bash
mkdir -p /tmp/sap_login
```

#### Step 4: Update Your Local MySQL Database

If you haven't set up your local MySQL database yet, run the MySQL migration file:

```bash
python mysql_migration_consolidated_final.py
```

This will create all the necessary tables including the SO Against Invoice module tables.

#### Step 5: Restart the Application

After creating the credential file, restart your local WMS application. You should see logs indicating:
- ✅ Credentials loaded from [path]
- ✅ MYSQL database connection successful

### Alternative: Environment Variables

If you prefer not to use the JSON file, you can set these environment variables instead:

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=your_mysql_username
export MYSQL_PASSWORD=your_mysql_password
export MYSQL_DATABASE=your_wms_database
export DATABASE_URL="mysql+pymysql://your_mysql_username:your_mysql_password@localhost:3306/your_wms_database"
export SESSION_SECRET="your-secure-session-secret-here"
```

### Troubleshooting

1. **Check the logs** for connection errors
2. **Verify MySQL is running** on your local machine
3. **Test database connection** using a MySQL client
4. **Check file permissions** on the credential JSON file
5. **Verify JSON syntax** is correct (no trailing commas, proper quotes)

### Verification

After setting up the credentials, check your application logs for:
```
✅ Credentials loaded from [your credential file path]
✅ MYSQL database connection successful
✅ Database tables created
✅ Default data initialized
✅ All module models verified/created
```

If you see warnings like "⚠️ Credential file not found" but the application still connects to your database, it means the application is falling back to environment variables, which is also acceptable.

### Note for SO Against Invoice Module

The SO Against Invoice module is now fully integrated with user management:
- **Permission Enforcement**: All routes now properly check for `so_against_invoice` permission
- **User Management UI**: Administrators can assign `so_against_invoice` permissions to users through the User Management interface  
- **Role-based Access**: Admin and Manager roles get `so_against_invoice` permission by default
- **API Security**: All API endpoints require proper permissions before processing requests

### Recent Updates

✅ **Permission System Enhanced** (September 17, 2025)
- Added proper permission checks to all SO Against Invoice routes (`/so-against-invoice/*`)
- Fixed inconsistent permission lists between user creation and editing
- Added SO Against Invoice checkbox to user management templates
- All API endpoints now return 403 for unauthorized access
- MySQL migration files verified to include all SO Against Invoice tables