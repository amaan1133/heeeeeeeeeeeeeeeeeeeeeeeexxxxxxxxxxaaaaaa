
from app import app
from models import db
from sqlalchemy import text, inspect

def setup_missing_tables():
    """Create any missing tables"""
    with app.app_context():
        try:
            # Create all tables from models
            db.create_all()
            
            # Check if Bill table exists, if not create it
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'bill' not in existing_tables:
                print("Creating Bill table...")
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
                        request_id INTEGER NOT NULL REFERENCES asset_request(id),
                        uploaded_by INTEGER NOT NULL REFERENCES user(id),
                        verified_by INTEGER REFERENCES user(id),
                        verified_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
            if 'inventory_update' not in existing_tables:
                print("Creating InventoryUpdate table...")
                db.session.execute(text("""
                    CREATE TABLE inventory_update (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        asset_id INTEGER NOT NULL REFERENCES asset(id),
                        previous_quantity INTEGER NOT NULL,
                        new_quantity INTEGER NOT NULL,
                        update_type VARCHAR(50) NOT NULL,
                        reason TEXT,
                        updated_by INTEGER NOT NULL REFERENCES user(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
            db.session.commit()
            print("All tables created successfully!")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            db.session.rollback()

if __name__ == '__main__':
    setup_missing_tables()
