
#!/usr/bin/env python3
"""
Test script to verify PostgreSQL connection
"""

import os
import psycopg2
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_psycopg2():
    """Test direct psycopg2 connection"""
    try:
        conn_string = "postgresql://hexamed:OuSKUPQTl0akpyyEBqq0pRHzRliwbwjU@dpg-d29l04mr433s739gju60-a.oregon-postgres.render.com/hexamed"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
        logger.info("✅ Direct psycopg2 connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ Direct psycopg2 connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    try:
        engine = create_engine("postgresql://hexamed:OuSKUPQTl0akpyyEBqq0pRHzRliwbwjU@dpg-d29l04mr433s739gju60-a.oregon-postgres.render.com/hexamed")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            logger.info(f"Connected to database: {db_name}")
        logger.info("✅ SQLAlchemy connection successful!")
        return True
    except Exception as e:
        logger.error(f"❌ SQLAlchemy connection failed: {e}")
        return False

def main():
    """Run all connection tests"""
    logger.info("Testing PostgreSQL connection...")
    
    psycopg2_success = test_direct_psycopg2()
    sqlalchemy_success = test_sqlalchemy_connection()
    
    if psycopg2_success and sqlalchemy_success:
        logger.info("🎉 All connection tests passed! Your PostgreSQL database is ready.")
    else:
        logger.error("⚠️  Some connection tests failed. Check your database configuration.")

if __name__ == '__main__':
    main()
