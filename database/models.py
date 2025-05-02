"""
Database models for the Energy Anomaly Detection application.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from database.connection import Base

class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    energy_data = relationship("EnergyData", back_populates="user")
    anomaly_results = relationship("AnomalyResult", back_populates="user")
    
    @property
    def password(self):
        """Password getter - raises exception as password shouldn't be readable."""
        raise AttributeError("Password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        """Password setter - hashes the password."""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verify password against stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class EnergyData(Base):
    """Energy consumption data model."""
    __tablename__ = "energy_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, index=True)
    consumption = Column(Float)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    occupancy = Column(Integer, nullable=True)
    day_of_week = Column(Integer, nullable=True)
    hour_of_day = Column(Integer, nullable=True)
    is_weekend = Column(Boolean, nullable=True)
    is_holiday = Column(Boolean, nullable=True)
    season = Column(String(20), nullable=True)
    device_id = Column(String(50), nullable=True)
    building_id = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="energy_data")
    anomaly_results = relationship("AnomalyResult", back_populates="energy_data")
    
    def to_dict(self):
        """Convert energy data to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "consumption": self.consumption,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "occupancy": self.occupancy,
            "day_of_week": self.day_of_week,
            "hour_of_day": self.hour_of_day,
            "is_weekend": self.is_weekend,
            "is_holiday": self.is_holiday,
            "season": self.season,
            "device_id": self.device_id,
            "building_id": self.building_id,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AnomalyResult(Base):
    """Anomaly detection results model."""
    __tablename__ = "anomaly_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    energy_data_id = Column(Integer, ForeignKey("energy_data.id"))
    model_name = Column(String(50))  # isolation_forest, autoencoder, etc.
    anomaly_score = Column(Float)
    is_anomaly = Column(Boolean)
    anomaly_type = Column(String(50), nullable=True)  # spike, drop, steady, etc.
    severity = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    recommendation = Column(Text, nullable=True)
    model_parameters = Column(JSON, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="anomaly_results")
    energy_data = relationship("EnergyData", back_populates="anomaly_results")
    
    def to_dict(self):
        """Convert anomaly result to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "energy_data_id": self.energy_data_id,
            "model_name": self.model_name,
            "anomaly_score": self.anomaly_score,
            "is_anomaly": self.is_anomaly,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "model_parameters": self.model_parameters,
            "execution_time_ms": self.execution_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }