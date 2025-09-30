#!/usr/bin/env python3
"""
Database migration script for the AI Audit Engine
"""

from app import app, db
from database import Audit, AuditFile, User

def run_migrations():
    """Run database migrations"""
    with app.app_context():
        print("🔄 Running database migrations...")
        
        # Create all tables
        db.create_all()
        
        print("[SUCCESS] Database migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()
