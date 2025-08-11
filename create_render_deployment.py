
#!/usr/bin/env python3
"""
Create a deployment-ready package for Render hosting
This will package the application with environment files instead of Replit secrets
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_deployment_package():
    """Create a complete deployment package for Render"""
    
    # Create deployment directory
    deployment_dir = "render_deployment"
    if os.path.exists(deployment_dir):
        shutil.rmtree(deployment_dir)
    os.makedirs(deployment_dir)
    
    # Files to include in deployment
    files_to_copy = [
        'main.py',
        'app.py', 
        'models.py',
        'routes.py',
        'gunicorn_config.py',
        'requirements.txt'
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
    
    # Create uploads directory with gitkeep
    uploads_dir = os.path.join(deployment_dir, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    with open(os.path.join(uploads_dir, '.gitkeep'), 'w') as f:
        f.write('')
    
    # Create .env file with Render PostgreSQL configuration
    env_content = """# Hexamed Asset Management System - Render Deployment
# Database Configuration (Render PostgreSQL)
DATABASE_URL=postgresql://hexamed:aN9CwJhCliBvNbz0VwGdf8ETvb9pM7GV@dpg-d2csqgoc8gjchc739os36g-a.oregon-postgres.render.com/hexamed_zxxw

# Flask Configuration
SECRET_KEY=hexamed-render-production-secret-key-change-this-in-production
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
    print("✅ Created .env file with Render PostgreSQL credentials")
    
    # Create render.yaml for Render deployment
    render_yaml = """services:
  - type: web
    name: hexamed-asset-management
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn --bind 0.0.0.0:$PORT --timeout 120 main:app"
    envVars:
      - key: DATABASE_URL
        value: postgresql://hexamed_6i8z_user:0VKd5SEHuTIu0lvPSk9WeghNvYf1GJQr@dpg-d2cqoc8gjchc739os36g-a.oregon-postgres.render.com/hexamed_6i8z
      - key: SECRET_KEY
        value: hexamed-render-production-secret-key-change-this-in-production
      - key: FLASK_ENV
        value: production
      - key: UPLOAD_FOLDER
        value: uploads
"""
    
    with open(os.path.join(deployment_dir, 'render.yaml'), 'w') as f:
        f.write(render_yaml)
    print("✅ Created render.yaml deployment configuration")
    
    # Create README for deployment
    readme_content = """# Hexamed Asset Management System - Render Deployment

## Quick Deploy on Render

1. **Upload this folder to GitHub** (or use Render's direct upload)
2. **Connect to Render**: 
   - Go to https://render.com
   - Click "New +" -> "Web Service"
   - Connect your GitHub repo or upload this folder
3. **Configure Environment Variables** (if not using render.yaml):
   - DATABASE_URL: `postgresql://hexamed_6i8z_user:0VKd5SEHuTIu0lvPSk9WeghNvYf1GJQr@dpg-d2cqoc8gjchc739os36g-a.oregon-postgres.render.com/hexamed_6i8z`
   - SECRET_KEY: `hexamed-render-production-secret-key-change-this-in-production`
   - FLASK_ENV: `production`
4. **Deploy Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT --timeout 120 main:app`

## Default Login Credentials

- **Admin**: username: `admin`, password: `hexamed123`
- **Accounts**: username: `accounts`, password: `accounts123`

## Database

This deployment uses your Render PostgreSQL database. The connection is configured in the .env file.

## Security Notes

- Change the SECRET_KEY in production
- Update default passwords after first login
- Configure proper firewall rules
- Enable HTTPS (Render provides this automatically)

## Support

For issues or questions, refer to the application documentation.
"""
    
    with open(os.path.join(deployment_dir, 'README.md'), 'w') as f:
        f.write(readme_content)
    print("✅ Created deployment README")
    
    # Create optimized requirements.txt for production
    prod_requirements = """Flask==3.0.3
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.31
Werkzeug==3.0.3
gunicorn==22.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.1
python-dateutil==2.9.0
email-validator==2.2.0
openpyxl==3.1.5
xlrd==2.0.1
pandas==2.2.2
"""
    
    with open(os.path.join(deployment_dir, 'requirements.txt'), 'w') as f:
        f.write(prod_requirements)
    print("✅ Created production requirements.txt")
    
    # Create the zip file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f"hexamed_render_deployment_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deployment_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deployment_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temporary directory
    shutil.rmtree(deployment_dir)
    
    print(f"\n🎉 Deployment package created: {zip_filename}")
    print(f"📦 Package size: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    print("\n📋 Next steps:")
    print("1. Download the zip file")
    print("2. Extract it or upload directly to Render")
    print("3. Deploy on Render using the included render.yaml")
    print("4. Your app will automatically connect to the Render PostgreSQL database")
    
    return zip_filename

if __name__ == '__main__':
    create_deployment_package()
