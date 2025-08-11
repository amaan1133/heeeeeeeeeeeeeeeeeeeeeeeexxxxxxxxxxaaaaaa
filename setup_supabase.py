
#!/usr/bin/env python3
"""
Setup script for Supabase PostgreSQL database
This will create all necessary tables and initialize data
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import *
from sqlalchemy import text, inspect
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_supabase_database():
    """Setup Supabase database with all tables and initial data"""
    
    with app.app_context():
        try:
            logger.info("Starting Supabase database setup...")
            
            # Test connection
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"Connected to: {version}")
            
            # Create all tables
            logger.info("Creating database tables...")
            db.create_all()
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                logger.info("Creating default admin user...")
                admin_user = User(
                    username='admin',
                    email='admin@hexamed.com',
                    full_name='System Administrator',
                    role='MD',
                    floor='Admin',
                    department='Administration'
                )
                admin_user.set_password('hexamed123')
                db.session.add(admin_user)
            
            # Create sample vendors if none exist
            if Vendor.query.count() == 0:
                logger.info("Creating sample vendors...")
                vendors = [
                    Vendor(
                        vendor_name='TechCorp Solutions',
                        contact_person='John Smith',
                        phone='+1-555-0101',
                        email='john@techcorp.com',
                        address='123 Tech Street, Silicon Valley, CA 94000',
                        vendor_code='TC001',
                        category='IT Equipment',
                        payment_terms='Net 30 days'
                    ),
                    Vendor(
                        vendor_name='Office Supplies Inc',
                        contact_person='Jane Doe',
                        phone='+1-555-0202',
                        email='jane@officesupplies.com',
                        address='456 Supply Avenue, Business City, NY 10001',
                        vendor_code='OS001',
                        category='Office Supplies',
                        payment_terms='Net 15 days'
                    ),
                    Vendor(
                        vendor_name='Furniture World',
                        contact_person='Mike Johnson',
                        phone='+1-555-0303',
                        email='mike@furnitureworld.com',
                        address='789 Furniture Blvd, Design Town, TX 75001',
                        vendor_code='FW001',
                        category='Furniture',
                        payment_terms='Net 30 days'
                    )
                ]
                
                for vendor in vendors:
                    db.session.add(vendor)
            
            # Create sample assets if none exist
            if Asset.query.count() == 0:
                logger.info("Creating sample assets...")
                assets = [
                    Asset(
                        asset_tag='HEXAMED-001',
                        name='Dell OptiPlex 7090',
                        category='IT Equipment',
                        asset_type='Fixed Asset',
                        brand='Dell',
                        model='OptiPlex 7090',
                        condition='Good',
                        location='Office Floor 1',
                        status='Available'
                    ),
                    Asset(
                        asset_tag='HEXAMED-002',
                        name='HP LaserJet Pro',
                        category='IT Equipment',
                        asset_type='Fixed Asset',
                        brand='HP',
                        model='LaserJet Pro M404n',
                        condition='Good',
                        location='Office Floor 1',
                        status='Available'
                    ),
                    Asset(
                        asset_tag='HEXAMED-003',
                        name='Office Paper A4',
                        category='Office Supplies',
                        asset_type='Consumable Asset',
                        current_quantity=100,
                        minimum_threshold=20,
                        unit_of_measurement='Ream',
                        location='Storage Room',
                        status='Available'
                    )
                ]
                
                for asset in assets:
                    db.session.add(asset)
            
            db.session.commit()
            logger.info("✅ Supabase database setup completed successfully!")
            logger.info("Default admin credentials:")
            logger.info("Username: admin")
            logger.info("Password: hexamed123")
            logger.info("Role: MD")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    if not os.environ.get('DATABASE_URL'):
        logger.error("❌ DATABASE_URL environment variable not set!")
        logger.error("Please update your .env file with your Supabase connection string")
        sys.exit(1)
    
    if setup_supabase_database():
        logger.info("🎉 Your application is ready to use with Supabase!")
    else:
        logger.error("❌ Setup failed. Please check your database connection.")
        sys.exit(1)
