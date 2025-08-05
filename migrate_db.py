
import os
from app import app, db
from sqlalchemy import text

def migrate_database():
    """Add missing columns to the database tables"""
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            asset_columns = [col['name'] for col in inspector.get_columns('asset')]
            asset_migrations = []
            
            if 'asset_type' not in asset_columns:
                asset_migrations.append("ALTER TABLE asset ADD COLUMN asset_type VARCHAR(50) DEFAULT 'Fixed Asset'")
            
            if 'current_quantity' not in asset_columns:
                asset_migrations.append("ALTER TABLE asset ADD COLUMN current_quantity INTEGER DEFAULT 1")
            
            if 'minimum_threshold' not in asset_columns:
                asset_migrations.append("ALTER TABLE asset ADD COLUMN minimum_threshold INTEGER DEFAULT 5")
            
            if 'unit_of_measurement' not in asset_columns:
                asset_migrations.append("ALTER TABLE asset ADD COLUMN unit_of_measurement VARCHAR(50) DEFAULT 'Piece'")
            
            # Check AssetRequest table columns
            request_columns = [col['name'] for col in inspector.get_columns('asset_request')]
            request_migrations = []
            
            if 'fulfilled_from_asset_id' not in request_columns:
                request_migrations.append("ALTER TABLE asset_request ADD COLUMN fulfilled_from_asset_id INTEGER")
            
            if 'fulfilled_quantity' not in request_columns:
                request_migrations.append("ALTER TABLE asset_request ADD COLUMN fulfilled_quantity INTEGER DEFAULT 0")
            
            if 'fulfilled_by' not in request_columns:
                request_migrations.append("ALTER TABLE asset_request ADD COLUMN fulfilled_by INTEGER")
            
            if 'fulfilled_at' not in request_columns:
                request_migrations.append("ALTER TABLE asset_request ADD COLUMN fulfilled_at TIMESTAMP")
            
            if 'fulfillment_notes' not in request_columns:
                request_migrations.append("ALTER TABLE asset_request ADD COLUMN fulfillment_notes TEXT")
            
            for migration in asset_migrations:
                print(f"Executing: {migration}")
                db.session.execute(text(migration))
            
            for migration in request_migrations:
                print(f"Executing: {migration}")
                db.session.execute(text(migration))
                        
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            user_migrations = []
            
            if 'floor' not in user_columns:
                user_migrations.append("ALTER TABLE user ADD COLUMN floor VARCHAR(50)")
            
            if 'department' not in user_columns:
                user_migrations.append("ALTER TABLE user ADD COLUMN department VARCHAR(100)")
            
            for migration in user_migrations:
                print(f"Executing: {migration}")
                db.session.execute(text(migration))
            
            if 'floor' not in request_columns:
                request_migrations.append("ALTER TABLE asset_request ADD COLUMN floor VARCHAR(50)")
            
            for migration in request_migrations:
                print(f"Executing: {migration}")
                db.session.execute(text(migration))

            db.session.commit()
            print("Database migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate_database()
