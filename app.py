import os
import sys
import logging
from flask import Flask

logging.basicConfig(level=logging.INFO)

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

    application_path = os.path.dirname(sys.executable)
    # Get database URL from environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    # Handle SQLite vs PostgreSQL URL format
    if DATABASE_URL.startswith('postgresql://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    upload_folder = os.getenv('UPLOAD_FOLDER', os.path.join(application_path, 'uploads'))
else:
    app = Flask(__name__)
    # Get database URL from environment variable
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    # Handle SQLite vs PostgreSQL URL format
    if DATABASE_URL.startswith('postgresql://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    else:
        # Fallback to SQLite for development
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    upload_folder = os.getenv('UPLOAD_FOLDER', os.path.join(os.getcwd(), 'uploads'))

logging.info(f"Database URL: {DATABASE_URL}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')


app.config['UPLOAD_FOLDER'] = upload_folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

from models import db

db.init_app(app)

import routes

with app.app_context():
    try:
        # Test database connection first
        with app.app_context():
            db.engine.connect()

        db.create_all()

        from models import User, Vendor
        from werkzeug.security import generate_password_hash

        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User()
            admin_user.username = 'admin'
            admin_user.email = 'admin@hexamed.com'
            admin_user.password_hash = generate_password_hash('hexamed123')
            admin_user.role = 'MD'
            admin_user.full_name = 'System Administrator'
            admin_user.floor = 'All'
            admin_user.department = 'Admin Block'
            db.session.add(admin_user)
            db.session.commit()
            logging.info("Admin user created with username: admin, password: hexamed123")

        accounts_user = User.query.filter_by(username='accounts').first()
        if not accounts_user:
            accounts_user = User()
            accounts_user.username = 'accounts'
            accounts_user.email = 'accounts@hexamed.com'
            accounts_user.password_hash = generate_password_hash('accounts123')
            accounts_user.role = 'Accounts/SCM'
            accounts_user.full_name = 'Accounts Manager'
            accounts_user.floor = 'All'
            accounts_user.department = 'Accounts'
            db.session.add(accounts_user)
            db.session.commit()
            logging.info("Accounts user created with username: accounts, password: accounts123")

        sample_vendors = [
            {
                'vendor_name': 'TechCorp Solutions',
                'vendor_code': 'TC001',
                'category': 'IT Equipment',
                'contact_person': 'amaan',
                'phone': '+91-9876543210',
                'email': 'sales@techcorp.com',
                'payment_terms': 'Net 30'
            },
            {
                'vendor_name': 'Office Furniture Ltd',
                'vendor_code': 'OF002',
                'category': 'Furniture',
                'contact_person': 'Sarah ',
                'phone': '+91-9876543211',
                'email': 'orders@officefurniture.com',
                'payment_terms': 'Net 15'
            },
            {
                'vendor_name': 'Medical Supplies Co',
                'vendor_code': 'MS003',
                'category': 'Medical Equipment',
                'contact_person': 'Dr. ritik ',
                'phone': '+91-9876543212',
                'email': 'info@medicalsupplies.com',
                'payment_terms': 'Advance'
            }
        ]

        for vendor_data in sample_vendors:
            existing_vendor = Vendor.query.filter_by(vendor_code=vendor_data['vendor_code']).first()
            if not existing_vendor:
                vendor = Vendor()
                for key, value in vendor_data.items():
                    setattr(vendor, key, value)
                db.session.add(vendor)

        db.session.commit()
        logging.info("Sample vendors created")

    except Exception as e:
        logging.error(f"Database initialization error: {e}")
        logging.info("App will start but database functionality may be limited")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

with app.app_context():
    print("\nAvailable Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:20s} -> {rule}")