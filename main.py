
import os
import sys
import logging
from sqlalchemy import inspect, text

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.chdir(application_path)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    base_path = getattr(sys, '_MEIPASS', application_path)
    data_path = application_path
else:
    base_path = application_path
    data_path = application_path

os.environ['DATABASE_URL'] = f'sqlite:///{os.path.join(data_path, "hexamed.db")}'
os.environ['UPLOAD_FOLDER'] = os.path.join(data_path, 'uploads')

uploads_dir = os.environ['UPLOAD_FOLDER']
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
    with open(os.path.join(uploads_dir, '.gitkeep'), 'w') as f:
        f.write('')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    import flask
    print(f"Flask version: {flask.__version__}")
    from app import app, db

    def create_tables_and_migrate():
        """Create database tables and add missing columns"""
        with app.app_context():
            try:
                # Create all tables first
                db.create_all()
                print("Created base tables")

                # Check and add missing columns to asset_request table
                inspector = inspect(db.engine)
                asset_request_columns = [col['name'] for col in inspector.get_columns('asset_request')]

                migrations = []
                
                if 'is_bulk_request' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN is_bulk_request BOOLEAN DEFAULT 0')
                    
                if 'bulk_items' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN bulk_items TEXT')
                    
                if 'item_classification' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN item_classification VARCHAR(20)')

                if 'floor' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN floor VARCHAR(50)')

                if 'fulfilled_from_asset_id' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN fulfilled_from_asset_id INTEGER')
                    
                if 'fulfilled_quantity' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN fulfilled_quantity INTEGER DEFAULT 0')
                    
                if 'fulfilled_by' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN fulfilled_by INTEGER')
                    
                if 'fulfilled_at' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN fulfilled_at TIMESTAMP')
                    
                if 'fulfillment_notes' not in asset_request_columns:
                    migrations.append('ALTER TABLE asset_request ADD COLUMN fulfillment_notes TEXT')

                # Check and add missing columns to user table
                user_columns = [col['name'] for col in inspector.get_columns('user')]
                
                if 'floor' not in user_columns:
                    migrations.append('ALTER TABLE user ADD COLUMN floor VARCHAR(50)')
                    
                if 'department' not in user_columns:
                    migrations.append('ALTER TABLE user ADD COLUMN department VARCHAR(100)')

                # Check and add missing columns to asset table
                asset_columns = [col['name'] for col in inspector.get_columns('asset')]
                
                if 'asset_type' not in asset_columns:
                    migrations.append("ALTER TABLE asset ADD COLUMN asset_type VARCHAR(50) DEFAULT 'Fixed Asset'")
                    
                if 'current_quantity' not in asset_columns:
                    migrations.append('ALTER TABLE asset ADD COLUMN current_quantity INTEGER DEFAULT 1')
                    
                if 'minimum_threshold' not in asset_columns:
                    migrations.append('ALTER TABLE asset ADD COLUMN minimum_threshold INTEGER DEFAULT 5')
                    
                if 'unit_of_measurement' not in asset_columns:
                    migrations.append("ALTER TABLE asset ADD COLUMN unit_of_measurement VARCHAR(50) DEFAULT 'Piece'")

                # Execute all migrations
                for migration in migrations:
                    try:
                        print(f"Executing: {migration}")
                        db.session.execute(text(migration))
                    except Exception as e:
                        print(f"Migration failed (might already exist): {e}")
                        continue

                # Create missing tables if they don't exist
                existing_tables = inspector.get_table_names()
                
                if 'bill' not in existing_tables:
                    print("Creating bill table...")
                    db.session.execute(text("""
                        CREATE TABLE bill (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            bill_number VARCHAR(100) UNIQUE NOT NULL,
                            vendor_name VARCHAR(200) NOT NULL,
                            bill_amount FLOAT NOT NULL,
                            bill_date DATE NOT NULL,
                            description TEXT,
                            bill_file_path VARCHAR(500),
                            bill_filename VARCHAR(255),
                            status VARCHAR(50) DEFAULT 'Pending',
                            verification_comments TEXT,
                            request_id INTEGER NOT NULL,
                            uploaded_by INTEGER NOT NULL,
                            verified_by INTEGER,
                            verified_at TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                if 'vendor' not in existing_tables:
                    print("Creating vendor table...")
                    db.session.execute(text("""
                        CREATE TABLE vendor (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            vendor_name VARCHAR(200) NOT NULL,
                            contact_person VARCHAR(100),
                            phone VARCHAR(20),
                            email VARCHAR(120),
                            address TEXT,
                            vendor_code VARCHAR(50) UNIQUE,
                            category VARCHAR(100),
                            payment_terms VARCHAR(100),
                            is_active BOOLEAN DEFAULT 1,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                if 'inventory_update' not in existing_tables:
                    print("Creating inventory_update table...")
                    db.session.execute(text("""
                        CREATE TABLE inventory_update (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            asset_id INTEGER NOT NULL,
                            previous_quantity INTEGER NOT NULL,
                            new_quantity INTEGER NOT NULL,
                            update_type VARCHAR(50) NOT NULL,
                            reason TEXT,
                            updated_by INTEGER NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                if 'item_assignment' not in existing_tables:
                    print("Creating item_assignment table...")
                    db.session.execute(text("""
                        CREATE TABLE item_assignment (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_name VARCHAR(200) NOT NULL,
                            quantity INTEGER NOT NULL,
                            vendor_id INTEGER NOT NULL,
                            assigned_by INTEGER NOT NULL,
                            assigned_to INTEGER NOT NULL,
                            expected_delivery_date DATE,
                            actual_delivery_date DATE,
                            delivery_status VARCHAR(50) DEFAULT 'Pending',
                            notes TEXT,
                            delivery_notes TEXT,
                            unit_price FLOAT,
                            total_amount FLOAT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                if 'asset_maintenance' not in existing_tables:
                    print("Creating asset_maintenance table...")
                    db.session.execute(text("""
                        CREATE TABLE asset_maintenance (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            asset_id INTEGER NOT NULL,
                            maintenance_type VARCHAR(50) NOT NULL,
                            scheduled_date DATE NOT NULL,
                            completed_date DATE,
                            cost FLOAT,
                            service_provider VARCHAR(200),
                            description TEXT NOT NULL,
                            status VARCHAR(50) DEFAULT 'Scheduled',
                            next_maintenance_date DATE,
                            maintenance_notes TEXT,
                            created_by INTEGER NOT NULL,
                            updated_by INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                if 'asset_depreciation' not in existing_tables:
                    print("Creating asset_depreciation table...")
                    db.session.execute(text("""
                        CREATE TABLE asset_depreciation (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            asset_id INTEGER NOT NULL,
                            depreciation_method VARCHAR(50) DEFAULT 'Straight Line',
                            useful_life_years INTEGER NOT NULL,
                            salvage_value FLOAT DEFAULT 0,
                            annual_depreciation FLOAT NOT NULL,
                            accumulated_depreciation FLOAT DEFAULT 0,
                            book_value FLOAT NOT NULL,
                            depreciation_start_date DATE NOT NULL,
                            last_calculated_date DATE,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                if 'warranty_alert' not in existing_tables:
                    print("Creating warranty_alert table...")
                    db.session.execute(text("""
                        CREATE TABLE warranty_alert (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            asset_id INTEGER NOT NULL,
                            alert_type VARCHAR(50) NOT NULL,
                            alert_date DATE NOT NULL,
                            message TEXT NOT NULL,
                            is_active BOOLEAN DEFAULT 1,
                            acknowledged_by INTEGER,
                            acknowledged_at TIMESTAMP,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                if 'procurement_quotation' not in existing_tables:
                    print("Creating procurement_quotation table...")
                    db.session.execute(text("""
                        CREATE TABLE procurement_quotation (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            request_id INTEGER NOT NULL,
                            vendor_id INTEGER NOT NULL,
                            quotation_number VARCHAR(100) UNIQUE NOT NULL,
                            quoted_price FLOAT NOT NULL,
                            quoted_quantity INTEGER NOT NULL,
                            delivery_timeline VARCHAR(100),
                            validity_period INTEGER DEFAULT 30,
                            payment_terms VARCHAR(200),
                            warranty_period VARCHAR(100),
                            specifications TEXT,
                            additional_costs FLOAT DEFAULT 0,
                            total_cost FLOAT NOT NULL,
                            status VARCHAR(50) DEFAULT 'Pending',
                            evaluation_score FLOAT,
                            evaluation_notes TEXT,
                            submitted_by INTEGER NOT NULL,
                            evaluated_by INTEGER,
                            quotation_file_path VARCHAR(500),
                            quotation_filename VARCHAR(255),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """))

                if 'purchase_order' not in existing_tables:
                    print("Creating purchase_order table...")
                    db.session.execute(text("""
                        CREATE TABLE purchase_order (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            po_number VARCHAR(100) UNIQUE NOT NULL,
                            item_type VARCHAR(20) NOT NULL,
                            item_name VARCHAR(200) NOT NULL,
                            item_description TEXT,
                            quantity INTEGER NOT NULL,
                            unit_price FLOAT NOT NULL,
                            total_amount FLOAT NOT NULL,
                            gst_percentage FLOAT DEFAULT 18.0,
                            gst_amount FLOAT NOT NULL,
                            grand_total FLOAT NOT NULL,
                            vendor_id INTEGER NOT NULL,
                            vendor_name VARCHAR(200) NOT NULL,
                            vendor_address TEXT,
                            vendor_gst VARCHAR(50),
                            status VARCHAR(50) DEFAULT 'Draft',
                            po_status VARCHAR(50) DEFAULT 'Created',
                            requires_md_approval BOOLEAN DEFAULT 0,
                            md_approved BOOLEAN DEFAULT 0,
                            md_comments TEXT,
                            approved_by_md INTEGER,
                            approved_at TIMESTAMP,
                            payment_terms VARCHAR(200) DEFAULT 'Net 30 days',
                            delivery_terms VARCHAR(200),
                            warranty_terms TEXT,
                            special_instructions TEXT,
                            quotation_files TEXT,
                            vendor_documents TEXT,
                            request_id INTEGER,
                            created_by INTEGER NOT NULL,
                            updated_by INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            po_date DATE DEFAULT (DATE('now')),
                            expected_delivery_date DATE
                        )
                    """))

                db.session.commit()
                print("Database migration completed successfully!")
                return True

            except Exception as e:
                print(f"Error during migration: {e}")
                db.session.rollback()
                return False

    if __name__ == '__main__':
        if create_tables_and_migrate():
            print("Starting Hexamed Asset Management System...")
            print(f"Database: {os.environ['DATABASE_URL']}")
            print(f"Uploads: {os.environ['UPLOAD_FOLDER']}")
            print("Access the application at: http://localhost:5000")
            print("Press Ctrl+C to stop the server")

            app.run(host='0.0.0.0', port=5000, debug=True)
        else:
            print("Database migration failed. Please check the logs.")
            input("Press Enter to exit...")
            sys.exit(1)

except Exception as e:
    print(f"Error starting application: {e}")
    logging.error(f"Application startup error: {e}", exc_info=True)
    input("Press Enter to exit...")
    sys.exit(1)
