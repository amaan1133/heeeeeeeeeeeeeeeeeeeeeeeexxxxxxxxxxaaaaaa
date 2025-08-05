
#!/usr/bin/env python3
"""
Migration script to move from SQLite to PostgreSQL
Run this after setting up PostgreSQL database and updating DATABASE_URL
"""

import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_sqlite_connection():
    """Get SQLite database connection"""
    return sqlite3.connect('hexamed.db')

def get_postgresql_connection():
    """Get PostgreSQL database connection"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg2.connect(database_url)

def migrate_table_data(sqlite_conn, pg_conn, table_name, columns_mapping=None):
    """
    Migrate data from SQLite table to PostgreSQL table
    
    Args:
        sqlite_conn: SQLite connection
        pg_conn: PostgreSQL connection
        table_name: Name of the table to migrate
        columns_mapping: Dict mapping SQLite columns to PostgreSQL columns
    """
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    try:
        # Get data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            logger.info(f"No data to migrate for table: {table_name}")
            return
        
        # Get column names
        column_names = [description[0] for description in sqlite_cursor.description]
        
        # Apply column mapping if provided
        if columns_mapping:
            column_names = [columns_mapping.get(col, col) for col in column_names]
        
        # Clear existing data in PostgreSQL table
        pg_cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE")
        
        # Insert data into PostgreSQL
        placeholders = ','.join(['%s'] * len(column_names))
        insert_query = f"INSERT INTO {table_name} ({','.join(column_names)}) VALUES ({placeholders})"
        
        pg_cursor.executemany(insert_query, rows)
        
        logger.info(f"Migrated {len(rows)} rows for table: {table_name}")
        
    except Exception as e:
        logger.error(f"Error migrating table {table_name}: {e}")
        raise

def update_sequences(pg_conn):
    """Update PostgreSQL sequences to match the current max IDs"""
    pg_cursor = pg_conn.cursor()
    
    tables_with_sequences = [
        'user', 'asset', 'asset_request', 'uploaded_file', 
        'approval', 'activity_log', 'bill', 'inventory_update'
    ]
    
    for table in tables_with_sequences:
        try:
            # Get max ID
            pg_cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
            max_id = pg_cursor.fetchone()[0]
            
            # Update sequence
            pg_cursor.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), {max_id + 1})")
            
            logger.info(f"Updated sequence for table {table} to {max_id + 1}")
            
        except Exception as e:
            logger.error(f"Error updating sequence for {table}: {e}")

def main():
    """Main migration function"""
    logger.info("Starting migration from SQLite to PostgreSQL...")
    
    # Check if SQLite database exists
    if not os.path.exists('hexamed.db'):
        logger.error("SQLite database 'hexamed.db' not found")
        return
    
    try:
        # Get connections
        sqlite_conn = get_sqlite_connection()
        pg_conn = get_postgresql_connection()
        
        # Migration order (respecting foreign key constraints)
        migration_order = [
            'user',
            'asset',
            'asset_request',
            'uploaded_file',
            'approval',
            'activity_log',
            'bill',
            'inventory_update'
        ]
        
        logger.info("Starting data migration...")
        
        for table in migration_order:
            try:
                migrate_table_data(sqlite_conn, pg_conn, table)
                pg_conn.commit()
            except Exception as e:
                logger.error(f"Failed to migrate table {table}: {e}")
                pg_conn.rollback()
                raise
        
        # Update sequences
        logger.info("Updating PostgreSQL sequences...")
        update_sequences(pg_conn)
        pg_conn.commit()
        
        logger.info("Migration completed successfully!")
        
        # Verification
        pg_cursor = pg_conn.cursor()
        for table in migration_order:
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = pg_cursor.fetchone()[0]
            logger.info(f"Table {table}: {count} rows")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == '__main__':
    main()
