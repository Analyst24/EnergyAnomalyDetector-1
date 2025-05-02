"""
Database migration utilities for the Energy Anomaly Detection application.
"""

import os
import json
from werkzeug.security import generate_password_hash

from database.connection import init_db, db_session
from database.models import User, EnergyData
from database.operations import create_user

def migrate_from_file_to_db():
    """
    Migrate existing data from files to database.
    
    This function:
    1. Migrates users from the JSON file to the database
    2. Migrates sample energy data to the database
    """
    # Initialize database tables
    init_db()
    
    # Migrate users
    migrate_users()
    
    # Migrate energy data
    # migrate_energy_data()
    
    print("Migration completed successfully")

def migrate_users():
    """Migrate users from JSON file to database."""
    users_file = 'data/users.json'
    
    # Check if users file exists
    if not os.path.exists(users_file):
        print(f"Users file {users_file} not found. Skipping user migration.")
        return
    
    # Load users from file
    try:
        with open(users_file, 'r') as f:
            users_data = json.load(f)
    except Exception as e:
        print(f"Error loading users file: {str(e)}")
        return
    
    # Migrate each user
    for user_data in users_data:
        username = user_data.get('username')
        email = user_data.get('email', f"{username}@example.com")
        password_hash = user_data.get('password')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists. Skipping.")
            continue
        
        # Create new user with existing password hash
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        db_session.add(user)
    
    # Commit changes
    db_session.commit()
    print(f"Migrated {len(users_data)} users to database")

def create_demo_users():
    """Create demo users in the database."""
    # Demo users
    demo_users = [
        {"username": "admin", "email": "admin@example.com", "password": "admin123"},
        {"username": "demo", "email": "demo@example.com", "password": "demo"}
    ]
    
    # Create each user
    for user_data in demo_users:
        username = user_data["username"]
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists. Skipping.")
            continue
        
        # Create new user
        create_user(
            username=username,
            email=user_data["email"],
            password=user_data["password"]
        )
    
    print(f"Created {len(demo_users)} demo users in database")

if __name__ == "__main__":
    # Run migration
    migrate_from_file_to_db()