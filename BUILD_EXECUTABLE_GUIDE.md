# 🚀 WMS Application - Executable Build Guide

## Problem Resolution
The error you encountered (`jinja2.exceptions.TemplateNotFound: login.html`) occurs because PyInstaller doesn't automatically include template files and static assets in the executable. This guide provides the complete solution.

## 📁 Files Created for You

1. **`build_exe.spec`** - PyInstaller specification file that includes all templates and static files
2. **`build_exe.bat`** - Windows batch script for easy building
3. **`build_exe.sh`** - Linux/macOS shell script for easy building
4. **`requirements_exe.txt`** - All dependencies needed for the executable

## 🔧 Quick Build Instructions

### For Windows:
```batch
# Simply run the batch file
build_exe.bat
```

### For Linux/macOS:
```bash
# Make the script executable and run it
chmod +x build_exe.sh
./build_exe.sh
```

### Manual Build (Alternative):
```bash
# Install PyInstaller
pip install pyinstaller

# Build using the spec file
pyinstaller --clean build_exe.spec
```

## ✅ What's Included in the Executable

The build process now includes:
- ✅ All HTML templates (`/templates/` directory)
- ✅ All static files (`/static/` directory) 
- ✅ Module templates (`/modules/*/templates/`)
- ✅ CSS, JavaScript, and image files
- ✅ All Python dependencies
- ✅ Database drivers (PostgreSQL, MySQL, ODBC)

## 🔧 Configuration for Deployment

### Database Configuration
The executable will look for database configuration in this order:
1. **JSON credential file**: `C:/tmp/sap_login/credential.json` (Windows) or `/tmp/sap_login/credential.json` (Linux)
2. **Environment variables**: DATABASE_URL, MYSQL_HOST, etc.
3. **Fallback**: Built-in defaults

### Required Directory Structure on Target Machine:
```
WMS_Application.exe          # Your executable
C:/tmp/sap_login/           # Credential directory
└── credential.json         # Your configuration file
```

### Sample credential.json:
```json
{
   "SAP_B1_SERVER": "https://192.168.0.134:50000",
   "SAP_B1_USERNAME": "manager", 
   "SAP_B1_PASSWORD": "your_password",
   "SAP_B1_COMPANY_DB": "your_company_db",
   "MYSQL_HOST": "localhost",
   "MYSQL_PORT": "3306",
   "MYSQL_USER": "root",
   "MYSQL_PASSWORD": "your_mysql_password",
   "MYSQL_DATABASE": "wms_db",
   "DATABASE_URL": "mysql+pymysql://user:password@host:port/database"
}
```

## 🚀 Running the Executable

1. **Place the executable** in your desired directory
2. **Create credential file** at `C:/tmp/sap_login/credential.json`
3. **Ensure database access** from the target machine
4. **Run the executable**: `./WMS_Application.exe`
5. **Access the application**: Open browser to `http://localhost:5000`

## 🔐 Default Login Credentials

- **Username**: admin
- **Password**: admin123

## 🎯 Key Features Included

- ✅ User authentication and management
- ✅ Inventory transfer operations
- ✅ Serial number tracking  
- ✅ SAP B1 integration
- ✅ Barcode/QR code generation
- ✅ Invoice creation module
- ✅ Pick list management
- ✅ GRPO functionality
- ✅ QC approval workflows

## 📋 Troubleshooting

### Issue: "Template not found" 
**Solution**: Use the provided `build_exe.spec` file instead of basic PyInstaller command

### Issue: "Module not found"
**Solution**: Install all requirements: `pip install -r requirements_exe.txt`

### Issue: Database connection failed
**Solution**: Verify credential.json file and database accessibility

### Issue: SAP connection failed
**Solution**: Check SAP B1 server accessibility and credentials

## 🔄 Updating the Executable

When you make code changes:
1. Run the build script again
2. The old executable will be replaced
3. Database and credentials remain the same

## 📝 Notes for Distribution

- The executable is **self-contained** with all dependencies
- **Database must be accessible** from target machines
- **SAP B1 server must be reachable** for full functionality  
- Templates and static files are **embedded in the executable**
- Default port is **5000** - ensure it's available

## 🆘 Support

If you encounter issues:
1. Check the console output for detailed error messages
2. Verify all file paths and permissions
3. Ensure database connectivity
4. Test SAP B1 integration separately if needed

The executable will create log files in `C:/tmp/wms_logs/` for debugging purposes.