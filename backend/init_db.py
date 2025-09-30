#!/usr/bin/env python3
"""
Database initialization script for the AI Audit Engine
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

def create_database():
    """Create the audit_db database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'audit_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("Creating database 'audit_db'...")
            cursor.execute("CREATE DATABASE audit_db")
            print("[SUCCESS] Database 'audit_db' created successfully")
        else:
            print("[SUCCESS] Database 'audit_db' already exists")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"[ERROR] Error creating database: {e}")
        sys.exit(1)

def test_connection():
    """Test connection to the audit_db database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="audit_db",
            user="postgres",
            password="password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"[SUCCESS] Connected to PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"[ERROR] Error connecting to database: {e}")
        return False

def main():
    """Main initialization function"""
    print("🔧 Database Initialization for AI Audit Engine")
    print("=" * 50)
    
    # Create database
    create_database()
    
    # Test connection
    if test_connection():
        print("\n[SUCCESS] Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the Flask application: python app.py")
        print("2. The database tables will be created automatically")
    else:
        print("\n[ERROR] Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()


