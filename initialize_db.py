"""
Initialize the database for the Energy Anomaly Detection application.
This script:
1. Creates all tables in the database
2. Migrates existing data (if any)
3. Creates demo users if needed
"""

import os
import sys

# Try to import database modules
try:
    from database.connection import init_db, test_connection
    from database.migration import migrate_from_file_to_db, create_demo_users
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Database modules not available, skipping database initialization")

def main():
    """Initialize database and perform migrations."""
    if not DATABASE_AVAILABLE:
        print("❌ Database modules not available, skipping initialization")
        return
        
    print("🔄 Testing database connection...")
    try:
        connection_status = test_connection()
        
        if connection_status["status"] != "connected":
            print(f"❌ Database connection failed: {connection_status['message']}")
            print("⚠️ Continuing without database connection verification")
        else:
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Error testing database connection: {str(e)}")
        print("⚠️ Continuing without database connection verification")
    
    # Initialize database tables
    print("🔄 Creating database tables...")
    init_db()
    print("✅ Database tables created successfully")
    
    # Migrate existing data
    print("🔄 Migrating existing data...")
    migrate_from_file_to_db()
    print("✅ Data migration completed")
    
    # Create demo users if needed
    print("🔄 Creating demo users...")
    create_demo_users()
    print("✅ Demo users created")
    
    print("✅ Database initialization completed successfully")

if __name__ == "__main__":
    main()