import pandas as pd
import numpy as np
from datetime import datetime

def preprocess_data(df):
    """
    Preprocess the energy consumption data:
    - Handle missing values
    - Convert data types
    - Extract features from timestamp
    - Create derived features
    
    Parameters:
    df (pd.DataFrame): Input DataFrame with energy consumption data
    
    Returns:
    pd.DataFrame: Preprocessed DataFrame
    """
    # Make a copy to avoid modifying the original
    data = df.copy()
    
    # Convert timestamp to datetime if it exists
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        # Extract time features
        data['hour'] = data['timestamp'].dt.hour
        data['day'] = data['timestamp'].dt.day
        data['month'] = data['timestamp'].dt.month
        data['year'] = data['timestamp'].dt.year
        data['dayofweek'] = data['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
        
        # Create time of day category
        data['time_of_day'] = pd.cut(
            data['hour'], 
            bins=[0, 6, 12, 18, 24], 
            labels=['night', 'morning', 'afternoon', 'evening'],
            include_lowest=True
        )
        
        # Create weekend flag
        data['is_weekend'] = (data['dayofweek'] >= 5).astype(int)
    
    # Handle missing values
    for col in data.columns:
        # For numeric columns, fill with median
        if data[col].dtype in ['int64', 'float64']:
            if data[col].isnull().sum() > 0:
                data[col] = data[col].fillna(data[col].median())
        
        # For categorical columns, fill with mode
        elif data[col].dtype == 'object' or data[col].dtype.name == 'category':
            if data[col].isnull().sum() > 0:
                data[col] = data[col].fillna(data[col].mode()[0])
    
    # If consumption column exists, create derived features
    if 'consumption' in data.columns:
        # Calculate rolling statistics for time series data if timestamp exists
        if 'timestamp' in data.columns:
            # Sort by timestamp to ensure correct rolling calculations
            data = data.sort_values('timestamp')
            
            # Calculate rolling mean and std of consumption (24-hour window)
            window_size = 24  # 24 hours
            data['consumption_rolling_mean'] = data['consumption'].rolling(window=window_size, min_periods=1).mean()
            data['consumption_rolling_std'] = data['consumption'].rolling(window=window_size, min_periods=1).std()
            
            # Calculate percent change from previous hour
            data['consumption_pct_change'] = data['consumption'].pct_change().fillna(0)
    
    # If temperature column exists, create derived features
    if 'temperature' in data.columns and 'consumption' in data.columns:
        # Create temperature efficiency ratio
        data['temp_consumption_ratio'] = data['consumption'] / (data['temperature'] + 1)  # Add 1 to avoid division by zero
    
    # Convert categorical variables to one-hot encoding
    cat_columns = data.select_dtypes(include=['object', 'category']).columns
    for col in cat_columns:
        # Skip timestamp column if it exists
        if col == 'timestamp':
            continue
            
        # Create dummies and add to dataframe
        dummies = pd.get_dummies(data[col], prefix=col, drop_first=True)
        data = pd.concat([data, dummies], axis=1)
    
    # Drop the original categorical columns
    data = data.drop(columns=cat_columns)
    
    # If timestamp exists, set it as index but keep it in the dataframe
    if 'timestamp' in data.columns:
        data = data.set_index('timestamp', drop=False)
    
    return data
