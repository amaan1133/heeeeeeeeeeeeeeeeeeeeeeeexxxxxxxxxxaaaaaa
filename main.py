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
    from app import app, db

    def create_tables():
        """Create database tables"""
        try:
            db.create_all()

            # Add new columns if they don't exist
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('asset_request')]

            if 'is_bulk_request' not in columns:
                db.session.execute(text('ALTER TABLE asset_request ADD COLUMN is_bulk_request BOOLEAN DEFAULT 0'))
                print("Added is_bulk_request column")

            if 'bulk_items' not in columns:
                db.session.execute(text('ALTER TABLE asset_request ADD COLUMN bulk_items TEXT'))
                print("Added bulk_items column")

            if 'item_classification' not in columns:
                db.session.execute(text('ALTER TABLE asset_request ADD COLUMN item_classification VARCHAR(20)'))
                print("Added item_classification column")

            db.session.commit()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return False
        return True

    if __name__ == '__main__':
        create_tables()
        print("Starting Hexamed Asset Management System...")
        print(f"Database: {os.environ['DATABASE_URL']}")
        print(f"Uploads: {os.environ['UPLOAD_FOLDER']}")
        print("Access the application at: http://localhost:5000")
        print("Press Ctrl+C to stop the server")

        app.run(host='0.0.0.0', port=5000, debug=True)

except Exception as e:
    print(f"Error starting application: {e}")
    logging.error(f"Application startup error: {e}", exc_info=True)
    input("Press Enter to exit...")
    sys.exit(1)