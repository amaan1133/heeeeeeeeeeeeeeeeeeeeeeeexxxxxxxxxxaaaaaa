
from app import app, db
from sqlalchemy import text

def create_item_assignment_table():
    """Create the item_assignment table"""
    with app.app_context():
        try:
            # Check if table exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if 'item_assignment' not in existing_tables:
                print("Creating ItemAssignment table...")
                
                # Create the item_assignment table
                db.session.execute(text("""
                    CREATE TABLE item_assignment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name VARCHAR(200) NOT NULL,
                        quantity INTEGER NOT NULL,
                        vendor_id INTEGER NOT NULL REFERENCES vendor(id),
                        assigned_by INTEGER NOT NULL REFERENCES user(id),
                        assigned_to INTEGER NOT NULL REFERENCES user(id),
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
                
                print("ItemAssignment table created successfully!")
            else:
                print("ItemAssignment table already exists")
            
            # Also create vendor table if it doesn't exist
            if 'vendor' not in existing_tables:
                print("Creating Vendor table...")
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
                print("Vendor table created successfully!")
                
            db.session.commit()
            print("All tables created successfully!")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_item_assignment_table()
