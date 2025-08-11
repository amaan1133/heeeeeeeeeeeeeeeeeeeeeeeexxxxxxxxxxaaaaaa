#!/usr/bin/env python3
"""
Test script to verify Render PostgreSQL connection
"""

import os
import psycopg2
from sqlalchemy import create_engine, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_render_connection():
    """Test Render PostgreSQL connection"""
    try:
        # Your new Render database URL
        conn_string = "postgresql://hexamed:aN9CwJhCliBvNbz0VwGdf8ETvb9pM7GV@dpg-d2csqgbuibrs738r93j0-a.oregon-postgres.render.com/hexamed_zxxw"

        # Test direct psycopg2 connection
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
        logger.info("✅ Direct psycopg2 connection successful!")

        # Test SQLAlchemy connection
        engine = create_engine(conn_string)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            logger.info(f"Connected to database: {db_name}")
        logger.info("✅ SQLAlchemy connection successful!")

        logger.info("🎉 Render PostgreSQL database is ready!")
        return True

    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False

if __name__ == '__main__':
    test_render_connection()