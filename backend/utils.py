import pandas as pd
import numpy as np

def detect_contradictions(data):
    """
    Detect contradictions and inconsistencies in energy consumption data
    
    Parameters:
    data (pd.DataFrame): Preprocessed energy data
    
    Returns:
    list: List of dictionaries containing contradiction details
    """
    contradictions = []
    
    # Check if necessary columns exist
    if 'consumption' not in data.columns:
        return contradictions
    
    # Contradiction 1: Zero consumption during working hours in industrial locations
    if all(col in data.columns for col in ['consumption', 'hour', 'location']):
        if 'location_industrial' in data.columns:
            industrial_mask = data['location_industrial'] == 1
            working_hours_mask = (data['hour'] >= 8) & (data['hour'] <= 17)
            zero_consumption_mask = data['consumption'] == 0
            
            contradictions_mask = industrial_mask & working_hours_mask & zero_consumption_mask
            
            if contradictions_mask.any():
                contradictions.append({
                    'type': 'zero_consumption_industrial_working_hours',
                    'count': int(contradictions_mask.sum()),
                    'indices': list(data.index[contradictions_mask]),
                    'message': 'Zero energy consumption detected during working hours at industrial locations'
                })
    
    # Contradiction 2: Extremely high consumption at night in residential areas
    if all(col in data.columns for col in ['consumption', 'time_of_day', 'location']):
        if 'location_residential' in data.columns and 'time_of_day_night' in data.columns:
            residential_mask = data['location_residential'] == 1
            night_mask = data['time_of_day_night'] == 1
            
            # Calculate threshold for "extremely high" (e.g., 3 standard deviations above the mean)
            mean_consumption = data.loc[residential_mask, 'consumption'].mean()
            std_consumption = data.loc[residential_mask, 'consumption'].std()
            high_threshold = mean_consumption + 3 * std_consumption
            
            high_consumption_mask = data['consumption'] > high_threshold
            
            contradictions_mask = residential_mask & night_mask & high_consumption_mask
            
            if contradictions_mask.any():
                contradictions.append({
                    'type': 'high_consumption_residential_night',
                    'count': int(contradictions_mask.sum()),
                    'indices': list(data.index[contradictions_mask]),
                    'message': f'Unusually high energy consumption (>{high_threshold:.2f}) detected during night hours in residential areas'
                })
    
    # Contradiction 3: Consumption doesn't correlate with temperature in expected ways
    if all(col in data.columns for col in ['consumption', 'temperature', 'season']):
        if 'season_summer' in data.columns:
            summer_mask = data['season_summer'] == 1
            high_temp_mask = data['temperature'] > 30  # Assuming temperature in Celsius
            low_consumption_mask = data['consumption'] < data['consumption'].quantile(0.25)
            
            contradictions_mask = summer_mask & high_temp_mask & low_consumption_mask
            
            if contradictions_mask.any():
                contradictions.append({
                    'type': 'low_consumption_high_temp_summer',
                    'count': int(contradictions_mask.sum()),
                    'indices': list(data.index[contradictions_mask]),
                    'message': 'Unusually low energy consumption detected during high temperature summer days'
                })
    
    return contradictions

def generate_recommendations(results):
    """
    Generate energy efficiency recommendations based on anomaly results
    
    Parameters:
    results (pd.DataFrame): DataFrame with anomaly detection results
    
    Returns:
    dict: Dictionary of recommendations categorized by type
    """
    recommendations = {
        'general': [],
        'specific': [],
        'alerts': []
    }
    
    # Check if anomalies were detected
    if 'anomaly' not in results.columns:
        recommendations['general'].append({
            'title': 'No anomaly analysis available',
            'description': 'Please run anomaly detection first to get recommendations.'
        })
        return recommendations
    
    # Get anomalies
    anomalies = results[results['anomaly'] == 1]
    
    # If no anomalies found
    if len(anomalies) == 0:
        recommendations['general'].append({
            'title': 'No anomalies detected',
            'description': 'Your energy consumption patterns appear normal. Continue monitoring for any changes.'
        })
        return recommendations
    
    # General recommendations based on anomaly count
    anomaly_percent = (len(anomalies) / len(results)) * 100
    
    if anomaly_percent > 10:
        recommendations['general'].append({
            'title': 'High anomaly rate detected',
            'description': f'{anomaly_percent:.1f}% of your data shows anomalous patterns. Consider a thorough energy audit.'
        })
    else:
        recommendations['general'].append({
            'title': 'Low anomaly rate detected',
            'description': f'{anomaly_percent:.1f}% of your data shows anomalous patterns. Monitor specific instances highlighted in the results.'
        })
    
    # Specific recommendations based on time patterns
    if 'hour' in anomalies.columns:
        # Check for anomalies during specific times of day
        hour_counts = anomalies['hour'].value_counts()
        peak_hour = hour_counts.idxmax()
        
        if peak_hour >= 9 and peak_hour <= 17:
            recommendations['specific'].append({
                'title': 'Working hours energy anomalies',
                'description': f'Most anomalies occur around {peak_hour}:00. Review equipment usage and settings during this time.'
            })
        elif peak_hour >= 22 or peak_hour <= 5:
            recommendations['specific'].append({
                'title': 'Night-time energy anomalies',
                'description': f'Unusual energy patterns detected during night hours (peak at {peak_hour}:00). Check for equipment left running overnight.'
            })
    
    # Temperature-based recommendations
    if 'temperature' in anomalies.columns:
        # Check correlations between temperature and consumption for anomalies
        high_temp_anomalies = anomalies[anomalies['temperature'] > anomalies['temperature'].quantile(0.75)]
        
        if len(high_temp_anomalies) > 0 and len(high_temp_anomalies) / len(anomalies) > 0.5:
            recommendations['specific'].append({
                'title': 'Temperature-related anomalies',
                'description': 'Many anomalies occur during high temperature periods. Review HVAC system efficiency and settings.'
            })
    
    # Location-based recommendations
    if 'location_industrial' in anomalies.columns and anomalies['location_industrial'].sum() > 0:
        industrial_anomalies = anomalies[anomalies['location_industrial'] == 1]
        if len(industrial_anomalies) > 0:
            recommendations['specific'].append({
                'title': 'Industrial location anomalies',
                'description': f'{len(industrial_anomalies)} anomalies detected in industrial locations. Consider equipment audits and operating schedule reviews.'
            })
    
    if 'location_residential' in anomalies.columns and anomalies['location_residential'].sum() > 0:
        residential_anomalies = anomalies[anomalies['location_residential'] == 1]
        if len(residential_anomalies) > 0:
            recommendations['specific'].append({
                'title': 'Residential location anomalies',
                'description': f'{len(residential_anomalies)} anomalies detected in residential locations. Check for unusual appliance usage patterns.'
            })
    
    # Generate alerts for highest anomaly scores
    if 'anomaly_score' in anomalies.columns:
        top_anomalies = anomalies.nlargest(3, 'anomaly_score')
        
        for _, row in top_anomalies.iterrows():
            alert = {
                'title': f'High severity anomaly detected',
                'description': f'Anomaly score: {row["anomaly_score"]:.2f}'
            }
            
            # Add timestamp if available
            if 'timestamp' in row:
                alert['description'] += f' at {row["timestamp"]}'
            
            # Add consumption if available
            if 'consumption' in row:
                alert['description'] += f', consumption: {row["consumption"]:.2f}'
            
            recommendations['alerts'].append(alert)
    
    return recommendations
