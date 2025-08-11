
#!/usr/bin/env python3
"""
Create a standalone deployment package for Render hosting
This creates a completely independent package that can be uploaded to Render
without any Replit dependencies
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_standalone_deployment():
    """Create a complete standalone deployment package for Render"""
    
    # Create deployment directory
    deployment_dir = "hexamed_render_standalone"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    # Files to include in deployment
    files_to_copy = [
        'main.py',
        'app.py', 
        'models.py',
        'routes.py',
        'gunicorn_config.py'
    ]
    
    # Directories to copy
    dirs_to_copy = [
        'templates',
        'static'
    ]
    
    # Copy files
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, deployment_dir)
            print(f"✅ Copied {file}")
    
    # Copy directories
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(deployment_dir, dir_name))
            print(f"✅ Copied {dir_name}/ directory")
    
    # Create uploads directory
    uploads_dir = os.path.join(deployment_dir, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    with open(os.path.join(uploads_dir, '.gitkeep'), 'w') as f:
        f.write('# Keep this directory for file uploads\n')
    
    # Create production requirements.txt
    prod_requirements = """Flask==3.1.1
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.41
Werkzeug==3.1.3
gunicorn==23.0.0
psycopg2-binary==2.9.10
python-dotenv==1.0.0
python-dateutil==2.8.2
email-validator==2.2.0
openpyxl==3.1.5
xlrd==2.0.2
pandas>=2.3.1
"""
    
    with open(os.path.join(deployment_dir, 'requirements.txt'), 'w') as f:
        f.write(prod_requirements)
    print("✅ Created production requirements.txt")
    
    # Create .env file with your database credentials
    env_content = """# Hexamed Asset Management System - Render Production
# Database Configuration (Your Render PostgreSQL)
DATABASE_URL=postgresql://hexamed:aN9CwJhCliBvNbz0VwGdf8ETvb9pM7GV@dpg-d2csqgbuibrs738r93j0-a.oregon-postgres.render.com/hexamed_zxxw

# Flask Configuration
SECRET_KEY=hexamed-render-production-key-2024-secure
FLASK_ENV=production

# Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Server Configuration
PORT=10000
HOST=0.0.0.0

# Application Settings
DEBUG=False
"""
    
    with open(os.path.join(deployment_dir, '.env'), 'w') as f:
        f.write(env_content)
    print("✅ Created .env file with database credentials")
    
    # Create render.yaml for automatic deployment
    render_yaml = """services:
  - type: web
    name: hexamed-asset-management
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 main:app"
    envVars:
      - key: DATABASE_URL
        value: postgresql://hexamed:aN9CwJhCliBvNbz0VwGdf8ETvb9pM7GV@dpg-d2csqgbuibrs738r93j0-a.oregon-postgres.render.com/hexamed_zxxw
      - key: SECRET_KEY
        value: hexamed-render-production-key-2024-secure
      - key: FLASK_ENV
        value: production
      - key: DEBUG
        value: "False"
"""
    
    with open(os.path.join(deployment_dir, 'render.yaml'), 'w') as f:
        f.write(render_yaml)
    print("✅ Created render.yaml for automatic deployment")
    
    # Create startup script
    startup_script = """#!/bin/bash
# Hexamed Asset Management System Startup Script
echo "Starting Hexamed Asset Management System..."
echo "Database: $DATABASE_URL"
gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 main:app
"""
    
    with open(os.path.join(deployment_dir, 'start.sh'), 'w') as f:
        f.write(startup_script)
    os.chmod(os.path.join(deployment_dir, 'start.sh'), 0o755)
    print("✅ Created startup script")
    
    # Create deployment README
    readme_content = """# Hexamed Asset Management System - Standalone Render Deployment

## Quick Deploy Instructions

### Method 1: Direct Upload to Render
1. **Compress this folder** into a ZIP file
2. **Go to Render**: https://render.com/dashboard
3. **Create New Web Service** → Upload from Computer
4. **Upload the ZIP file**
5. **Render will automatically detect** the render.yaml and deploy

### Method 2: GitHub Upload
1. **Create a new GitHub repository**
2. **Upload all files** from this folder to the repository
3. **Connect repository to Render**
4. **Deploy automatically**

### Method 3: Manual Configuration
If render.yaml doesn't work, use these manual settings:

**Build Settings:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 main:app`

**Environment Variables:**
```
DATABASE_URL=postgresql://hexamed:aN9CwJhCliBvNbz0VwGdf8ETvb9pM7GV@dpg-d2csqgbuibrs738r93j0-a.oregon-postgres.render.com/hexamed_zxxw
SECRET_KEY=hexamed-render-production-key-2024-secure
FLASK_ENV=production
DEBUG=False
```

## Application Features

✅ **Complete Asset Management System**
✅ **PostgreSQL Database (Your Render DB)**
✅ **User Authentication & Roles**
✅ **Asset Tracking & Requests**
✅ **Purchase Order Management**
✅ **Vendor Management**
✅ **File Upload Support**
✅ **Reporting & Analytics**

## Default Login Credentials

After deployment, use these credentials:

**Administrator Account:**
- Username: `admin`
- Password: `hexamed123`

**Accounts/SCM Account:**
- Username: `accounts`
- Password: `accounts123`

⚠️ **Important:** Change these passwords after first login!

## Database

This deployment uses your Render PostgreSQL database:
- Database: hexamed_zxxw
- Host: dpg-d2csqgbuibrs738r93j0-a.oregon-postgres.render.com
- All credentials are embedded in the .env file

## Support

The application will automatically:
1. Connect to your PostgreSQL database
2. Create all necessary tables
3. Set up default users and vendors
4. Start the web server

## Security Notes

- All secrets are stored in environment files
- Database credentials are embedded for standalone deployment
- HTTPS is automatically provided by Render
- Change default passwords after deployment

## Troubleshooting

If deployment fails:
1. Check the build logs in Render dashboard
2. Verify database connection string
3. Ensure all files are uploaded correctly

This package is completely independent and ready for production deployment on Render.
"""
    
    with open(os.path.join(deployment_dir, 'README.md'), 'w') as f:
        f.write(readme_content)
    print("✅ Created comprehensive deployment README")
    
    # Create Procfile for additional compatibility
    procfile_content = "web: gunicorn --bind 0.0.0.0:$PORT --timeout 120 --workers 1 main:app"
    with open(os.path.join(deployment_dir, 'Procfile'), 'w') as f:
        f.write(procfile_content)
    print("✅ Created Procfile")
    
    # Create runtime.txt
    with open(os.path.join(deployment_dir, 'runtime.txt'), 'w') as f:
        f.write('python-3.11.6')
    print("✅ Created runtime.txt")
    
    # Create the deployment ZIP file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"hexamed_render_standalone_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
    
    # Get the size
    zip_size_mb = os.path.getsize(zip_filename) / 1024 / 1024
    
    # Clean up temporary directory
    shutil.rmtree(deployment_dir)
    
    print(f"\n🎉 STANDALONE DEPLOYMENT PACKAGE CREATED!")
    print(f"📦 Package: {zip_filename}")
    print(f"📊 Size: {zip_size_mb:.2f} MB")
    print(f"🗄️  Database: Your Render PostgreSQL")
    print(f"🔗 Connection: Embedded in package")
    
    print("\n📋 DEPLOYMENT OPTIONS:")
    print("1. 📤 Upload ZIP directly to Render")
    print("2. 📁 Extract and upload to GitHub, then connect to Render")
    print("3. 🔧 Use manual configuration with provided settings")
    
    print(f"\n✅ This package is completely independent of Replit!")
    print(f"✅ All credentials and dependencies are included!")
    print(f"✅ Ready for production deployment on Render!")
    
    return zip_filename

if __name__ == '__main__':
    create_standalone_deployment()
