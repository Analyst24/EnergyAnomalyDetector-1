"""
Database connection management module.
Manages SQLAlchemy sessions and database connections.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Get database URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Create base class for models
Base = declarative_base()
Base.query = db_session.query_property()

# For debugging database connection
def test_connection():
    """Test database connection and return status."""
    try:
        # Attempt a simple query to test connection
        engine.execute("SELECT 1")
        return {"status": "connected", "message": "Successfully connected to the database"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to connect to database: {str(e)}"}

# Use this to get a database session
def get_db():
    """Create and yield a database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Initialize database (create tables)
def init_db():
    """Initialize the database, creating all tables."""
    # Import all models here to ensure they are registered with the Base
    from database.models import User, EnergyData, AnomalyResult
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")