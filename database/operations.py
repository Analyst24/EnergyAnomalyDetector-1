"""
Database operations for the Energy Anomaly Detection application.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

from database.connection import db_session
from database.models import User, EnergyData, AnomalyResult

# User operations
def create_user(username: str, email: str, password: str) -> User:
    """
    Create a new user in the database.
    
    Parameters:
    username (str): User's username
    email (str): User's email
    password (str): User's password
    
    Returns:
    User: Created user object
    """
    user = User(username=username, email=email)
    user.password = password
    
    db_session.add(user)
    db_session.commit()
    return user

def get_user_by_username(username: str) -> Optional[User]:
    """
    Get user by username.
    
    Parameters:
    username (str): Username to search for
    
    Returns:
    Optional[User]: User object if found, None otherwise
    """
    return User.query.filter_by(username=username).first()

def get_user_by_email(email: str) -> Optional[User]:
    """
    Get user by email.
    
    Parameters:
    email (str): Email to search for
    
    Returns:
    Optional[User]: User object if found, None otherwise
    """
    return User.query.filter_by(email=email).first()

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password.
    
    Parameters:
    username (str): Username
    password (str): Password
    
    Returns:
    Optional[User]: User object if authentication succeeds, None otherwise
    """
    user = get_user_by_username(username)
    if user and user.verify_password(password):
        return user
    return None

# Energy data operations
def bulk_insert_energy_data(user_id: int, data_df: pd.DataFrame) -> List[EnergyData]:
    """
    Bulk insert energy data from DataFrame.
    
    Parameters:
    user_id (int): User ID associated with the data
    data_df (pd.DataFrame): DataFrame containing energy data
    
    Returns:
    List[EnergyData]: List of created energy data objects
    """
    energy_data_objects = []
    
    # Convert DataFrame to list of dictionaries
    for _, row in data_df.iterrows():
        # Extract data from DataFrame row
        data_dict = {
            "user_id": user_id,
            "timestamp": row.get("timestamp"),
            "consumption": row.get("consumption"),
            "temperature": row.get("temperature"),
            "humidity": row.get("humidity"),
            "occupancy": row.get("occupancy"),
            "day_of_week": row.get("day_of_week"),
            "hour_of_day": row.get("hour_of_day"),
            "is_weekend": row.get("is_weekend"),
            "is_holiday": row.get("is_holiday"),
            "season": row.get("season"),
            "device_id": row.get("device_id"),
            "building_id": row.get("building_id"),
            "notes": row.get("notes")
        }
        
        # Remove None values to use defaults
        data_dict = {k: v for k, v in data_dict.items() if v is not None}
        
        # Create EnergyData object
        energy_data = EnergyData(**data_dict)
        energy_data_objects.append(energy_data)
    
    # Bulk insert
    db_session.add_all(energy_data_objects)
    db_session.commit()
    
    return energy_data_objects

def get_energy_data_for_user(user_id: int, limit: int = 1000) -> List[EnergyData]:
    """
    Get energy data for a specific user.
    
    Parameters:
    user_id (int): User ID
    limit (int): Maximum number of records to return
    
    Returns:
    List[EnergyData]: List of energy data objects
    """
    return EnergyData.query.filter_by(user_id=user_id).order_by(EnergyData.timestamp.desc()).limit(limit).all()

def get_energy_data_as_dataframe(user_id: int, limit: int = 1000) -> pd.DataFrame:
    """
    Get energy data for a specific user as pandas DataFrame.
    
    Parameters:
    user_id (int): User ID
    limit (int): Maximum number of records to return
    
    Returns:
    pd.DataFrame: DataFrame containing energy data
    """
    energy_data = get_energy_data_for_user(user_id, limit)
    
    # Convert to list of dictionaries
    data_dicts = [data.to_dict() for data in energy_data]
    
    # Create DataFrame
    df = pd.DataFrame(data_dicts)
    
    # Convert timestamp strings back to datetime objects
    if 'timestamp' in df.columns and not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

# Anomaly result operations
def save_anomaly_results(user_id: int, results_df: pd.DataFrame, model_name: str) -> List[AnomalyResult]:
    """
    Save anomaly detection results to database.
    
    Parameters:
    user_id (int): User ID
    results_df (pd.DataFrame): DataFrame containing anomaly detection results
    model_name (str): Name of model used for detection
    
    Returns:
    List[AnomalyResult]: List of created anomaly result objects
    """
    anomaly_objects = []
    
    for _, row in results_df.iterrows():
        # Get the energy data id
        energy_data_id = row.get("id")
        
        # Create anomaly result
        anomaly_result = AnomalyResult(
            user_id=user_id,
            energy_data_id=energy_data_id,
            model_name=model_name,
            anomaly_score=row.get("anomaly_score"),
            is_anomaly=row.get("is_anomaly", False),
            anomaly_type=row.get("anomaly_type"),
            severity=row.get("severity"),
            confidence=row.get("confidence"),
            recommendation=row.get("recommendation"),
            model_parameters=row.get("model_parameters"),
            execution_time_ms=row.get("execution_time_ms")
        )
        
        anomaly_objects.append(anomaly_result)
    
    # Bulk insert
    db_session.add_all(anomaly_objects)
    db_session.commit()
    
    return anomaly_objects

def get_anomaly_results_for_user(user_id: int, limit: int = 1000) -> List[AnomalyResult]:
    """
    Get anomaly results for a specific user.
    
    Parameters:
    user_id (int): User ID
    limit (int): Maximum number of records to return
    
    Returns:
    List[AnomalyResult]: List of anomaly result objects
    """
    return AnomalyResult.query.filter_by(user_id=user_id).order_by(AnomalyResult.created_at.desc()).limit(limit).all()

def get_anomaly_results_as_dataframe(user_id: int, limit: int = 1000) -> pd.DataFrame:
    """
    Get anomaly results for a specific user as pandas DataFrame.
    
    Parameters:
    user_id (int): User ID
    limit (int): Maximum number of records to return
    
    Returns:
    pd.DataFrame: DataFrame containing anomaly results
    """
    anomaly_results = get_anomaly_results_for_user(user_id, limit)
    
    # Convert to list of dictionaries
    result_dicts = [result.to_dict() for result in anomaly_results]
    
    # Create DataFrame
    df = pd.DataFrame(result_dicts)
    
    return df