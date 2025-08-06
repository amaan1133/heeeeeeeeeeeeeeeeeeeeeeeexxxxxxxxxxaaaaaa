
#!/usr/bin/env python3
"""
Build script for Hexamed Asset Management System
Creates both portable ZIP package and compiled executable
"""

import os
import shutil
import zipfile
import subprocess
import sys
from datetime import datetime

def create_compiled_executable():
    """Create standalone executable using PyInstaller"""
    
    print("Hexamed Asset Management System - Build Script")
    print("=" * 50)
    
    print("Cleaning previous builds...")
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("  Cleaned build")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("  Cleaned dist")
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Create icon if it doesn't exist
    if not os.path.exists('generated-icon.png'):
        print("Creating app icon...")
        create_app_icon()
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                   
        '--windowed',                  
        '--name=HexamedAssetManagement', 
        '--icon=generated-icon.png',    
        '--add-data=templates:templates',  
        '--add-data=static:static',    # Include specific static folder (if needed)
        '--add-data=uploads:uploads',   # Include uploads folder
        '--hidden-import=flask',
        '--hidden-import=flask_sqlalchemy',#Include hidden imports
        '--hidden-import=werkzeug',         #Include all uploaded files
        '--hidden-import=sqlalchemy',
        '--hidden-import=openpyxl',
        '--hidden-import=pandas',
        '--hidden-import=xlrd',
        '--hidden-import=email_validator',
        'main.py'
    ]
    
    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("Build successful!")
        
        # Check if executable was created
        exe_path = os.path.join('dist', 'HexamedAssetManagement.exe')
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / 1024 / 1024
            print(f"✅ Executable created: {exe_path}")
            print(f"📦 Size: {size_mb:.2f} MB")
            return exe_path
        else:
            print("❌ Executable not found. Build may have failed.")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return None

def create_app_icon():
    """Create a simple app icon"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (256, 256), color='#2c3e50')
        draw = ImageDraw.Draw(img)
        
         
        draw.rectangle([78, 108, 178, 148], fill='white')
         
        draw.rectangle([108, 78, 148, 178], fill='white')

        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((128, 200), "HAM", anchor="mm", fill='white', font=font)
        
        img.save('generated-icon.png')
        print("  Icon created successfully")
        
    except ImportError:
        print("  PIL not available, using default icon")
    except Exception as e:
        print(f"  Icon creation failed: {e}")

def create_portable_package():
    """Create a portable ZIP package"""
    
    package_name = f"HexamedAssetManagement_Portable_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_dir = f"temp_{package_name}"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    print(f"Creating portable package: {package_name}")
    
    files_to_copy = [
        'main.py',
        'app.py', 
        'models.py',
        'routes.py',
        'requirements.txt'
    ]
    
    dirs_to_copy = [
        'templates',
        'static',
        'uploads'
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, temp_dir)
            print(f"  Copied: {file_name}")
    
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(temp_dir, dir_name))
            print(f"  Copied: {dir_name}/")
    
    create_startup_scripts(temp_dir)
    
    create_readme(temp_dir)
    
    zip_filename = f"{package_name}.zip"
    create_zip(temp_dir, zip_filename)
    
    shutil.rmtree(temp_dir)
    
    print(f"\n✅ Package created successfully: {zip_filename}")
    print(f"📦 Size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    return zip_filename

def create_startup_scripts(temp_dir):
    """Create startup scripts for different operating systems"""
    
    windows_script = """@echo off
echo Starting Hexamed Asset Management System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or later from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start the application
echo.
echo Starting application...
echo Access the application at: http://localhost:5000
echo.
echo Login credentials:
echo   Admin: admin / hexamed123
echo   Accounts: accounts / accounts123
echo.
echo Press Ctrl+C to stop the server
python main.py

pause
"""
    
    with open(os.path.join(temp_dir, 'start_windows.bat'), 'w') as f:
        f.write(windows_script)
    
    unix_script = """#!/bin/bash
echo "Starting Hexamed Asset Management System..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7 or later"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Start the application
echo
echo "Starting application..."
echo "Access the application at: http://localhost:5000"
echo
echo "Login credentials:"
echo "  Admin: admin / hexamed123"
echo "  Accounts: accounts / accounts123"
echo
echo "Press Ctrl+C to stop the server"
python3 main.py
"""
    
    with open(os.path.join(temp_dir, 'start_unix.sh'), 'w') as f:
        f.write(unix_script)
    
    os.chmod(os.path.join(temp_dir, 'start_unix.sh'), 0o755)

def create_readme(temp_dir):
    """Create README file with instructions"""
    
    readme_content = """# Hexamed Asset Management System - Portable Version

## Quick Start

### Windows Users:
1. Double-click `start_windows.bat`
2. Wait for dependencies to install
3. Open browser and go to: http://localhost:5000

### Mac/Linux Users:
1. Open terminal in this folder
2. Run: `./start_unix.sh`
3. Open browser and go to: http://localhost:5000

## Login Credentials
- **Admin**: username=`admin`, password=`hexamed123`
- **Accounts**: username=`accounts`, password=`accounts123`

## System Requirements
- Python 3.7 or later
- Internet connection (for initial setup only)
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Features
✅ Complete asset management system
✅ Multi-level approval workflow
✅ Bill tracking and verification
✅ Inventory management with consumables
✅ User management with role-based access
✅ Activity logging and audit trails
✅ Vendor management
✅ Item assignments and delivery tracking
✅ Excel/CSV export functionality
✅ Bulk upload capabilities

## Data Storage
- Database file (`hexamed.db`) stores all application data
- Uploaded files stored in `uploads/` folder
- All data persists between application restarts
- Portable - copy entire folder to backup/transfer data

## Security Features
- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- File upload restrictions
- Activity logging for audit trails

## User Roles & Permissions

### MD (Managing Director)
- Full system access
- Can approve requests at any level
- User management
- System configuration

### Admin
- User management
- Asset management
- Request approvals (level-based)
- System reports

### Accounts/SCM (Supply Chain Management)
- Asset and inventory management
- Vendor management
- Bill upload and tracking
- Request fulfillment
- Item assignments

### Concern Manager
- Department-specific approvals
- View floor-specific requests
- Asset requests

### User/Employee
- Submit asset requests
- Track request status
- View assigned assets

## Troubleshooting

### Application won't start:
1. Ensure Python 3.7+ is installed: `python --version`
2. Install dependencies manually: `pip install flask flask-sqlalchemy werkzeug pandas openpyxl`
3. Run manually: `python main.py`

### Can't access in browser:
1. Check if application started without errors
2. Try: http://127.0.0.1:5000
3. Ensure no firewall blocking port 5000

### Database issues:
1. Delete `hexamed.db` to reset (loses all data)
2. Application will recreate with default users

### File upload issues:
1. Ensure `uploads/` folder exists and is writable
2. Check file size (max 16MB)
3. Verify file type is allowed (PDF, images, documents)

## Support
This is a standalone application. No external services required.
All data stored locally for privacy and security.

## Version Information
Package created: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
Python Flask Application
SQLite Database
Bootstrap 5 UI Framework
"""
    
    with open(os.path.join(temp_dir, 'README.txt'), 'w') as f:
        f.write(readme_content)

def create_zip(source_dir, zip_filename):
    """Create ZIP file from directory"""
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arc_name)
                print(f"    Added to ZIP: {arc_name}")

def create_standalone_package(exe_path):
    """Create package with compiled executable"""
    
    package_name = f"HexamedAssetManagement_Standalone_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_dir = f"temp_{package_name}"
    
    # Create temporary directory
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    print(f"Creating standalone package: {package_name}")
    
    # Copy executable
    if exe_path and os.path.exists(exe_path):
        exe_name = 'HexamedAssetManagement.exe'
        shutil.copy2(exe_path, os.path.join(temp_dir, exe_name))
        print(f"  Copied: {exe_name}")
    
    # Create startup batch file
    startup_script = """@echo off
title Hexamed Asset Management System
echo.
echo ===================================================
echo  Hexamed Asset Management System
echo ===================================================
echo.
echo Starting application...
echo The web interface will open automatically.
echo.
echo Access URL: http://localhost:5000
echo.
echo Login Credentials:
echo   Admin: admin / hexamed123
echo   Accounts: accounts / accounts123
echo.
echo Press Ctrl+C to stop the application
echo.

start "" "http://localhost:5000"
HexamedAssetManagement.exe

pause
"""
    
    with open(os.path.join(temp_dir, 'Start_Hexamed.bat'), 'w') as f:
        f.write(startup_script)
    
    # Create README
    readme_content = """# Hexamed Asset Management System - Standalone Version

## Quick Start
1. Double-click 'Start_Hexamed.bat'
2. Your web browser will open automatically
3. Login with: admin / hexamed123

## Features
✅ No Python installation required
✅ No dependencies needed
✅ Completely portable
✅ Full asset management system
✅ Runs entirely offline

## System Requirements
- Windows 7 or later
- 100MB free disk space
- Modern web browser

## Data Storage
- All data stored in 'hexamed.db' file
- Uploaded files in 'uploads' folder
- Portable - copy entire folder to backup

Created: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
"""
    
    with open(os.path.join(temp_dir, 'README.txt'), 'w') as f:
        f.write(readme_content)
    
    zip_filename = f"{package_name}.zip"
    create_zip(temp_dir, zip_filename)
    
    shutil.rmtree(temp_dir)
    
    print(f"\n✅ Standalone package created: {zip_filename}")
    print(f"📦 Size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    return zip_filename

def main():
    print("Hexamed Asset Management System - Build Options")
    print("=" * 60)
    
    print("\n🔨 Creating compiled executable...")
    exe_path = create_compiled_executable()
    
    if exe_path:
        standalone_zip = create_standalone_package(exe_path)
        
        print("\n" + "=" * 60)
        print("🎉 COMPILATION COMPLETED SUCCESSFULLY!")
        print(f"📁 Executable: {exe_path}")
        print(f"📦 Standalone Package: {standalone_zip}")
        print("\n🚀 Download the ZIP file and run on any Windows computer!")
        print("   No Python installation required!")
        
    else:
        print("\n⚠️  Compilation failed, creating portable package instead...")
        try:
            zip_file = create_portable_package()
            print(f"\n✅ Portable package created: {zip_file}")
            print("   Requires Python to be installed on target computer")
        except Exception as e:
            print(f"❌ Error creating package: {e}")
            return False
    
    return True

if __name__ == '__main__':
    main()
