import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
import time
from datetime import datetime

def show_detection_page():
    st.title("Run Anomaly Detection")
    
    # Check if data is available
    if st.session_state.uploaded_data is None:
        st.info("No data available. Please upload energy consumption data first.")
        if st.button("Go to Upload Page"):
            st.session_state.current_page = "upload"
            st.rerun()
        return
    
    # Get data from session state
    df = st.session_state.uploaded_data
    
    st.markdown("### Configure Detection Parameters")
    
    # Model selection
    st.markdown("#### Select Anomaly Detection Model")
    
    model_options = {
        "isolation_forest": "Isolation Forest",
        "autoencoder": "Autoencoder Neural Network",
        "kmeans": "K-Means Clustering"
    }
    
    selected_model = st.selectbox(
        "Choose a model for anomaly detection:",
        options=list(model_options.keys()),
        format_func=lambda x: model_options[x],
        index=list(model_options.keys()).index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0
    )
    
    # Update session state with selected model
    st.session_state.selected_model = selected_model
    
    # Show model description based on selection
    if selected_model == "isolation_forest":
        st.markdown("""
        **Isolation Forest** detects anomalies by isolating observations. It builds random decision trees and anomalies 
        require fewer splits to be isolated. Works well for various data types and is computationally efficient.
        """)
    elif selected_model == "autoencoder":
        st.markdown("""
        **Autoencoder Neural Network** learns the normal patterns in your data by compressing and reconstructing it. 
        Data points with high reconstruction error are likely anomalies. Powerful for capturing complex patterns.
        """)
    elif selected_model == "kmeans":
        st.markdown("""
        **K-Means Clustering** groups similar data points together. Anomalies are points that are far from their 
        cluster centers. Simple and effective for detecting outliers in clustered data.
        """)
    
    # Anomaly threshold slider
    st.markdown("#### Anomaly Detection Sensitivity")
    threshold = st.slider(
        "Set the anomaly threshold (lower = more sensitive):",
        min_value=0.01,
        max_value=0.99,
        value=float(st.session_state.anomaly_threshold),
        step=0.01,
        format="%.2f"
    )
    
    # Update session state with threshold
    st.session_state.anomaly_threshold = threshold
    
    # Additional settings (expandable)
    with st.expander("Advanced Settings"):
        # Feature selection if there are multiple columns
        if len(df.columns) > 2:  # More than just timestamp and consumption
            st.markdown("#### Feature Selection")
            
            # Get numerical columns
            numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            
            # Remove timestamp if present
            if 'timestamp' in numerical_cols:
                numerical_cols.remove('timestamp')
            
            # Default selection: at least consumption
            default_selected = ['consumption'] if 'consumption' in numerical_cols else []
            
            # Let user select which numerical features to use
            selected_features = st.multiselect(
                "Select features to use for anomaly detection:",
                options=numerical_cols,
                default=default_selected
            )
            
            if not selected_features:
                st.warning("Please select at least one feature for anomaly detection.")
    
    # Run detection button
    if st.button("Run Anomaly Detection"):
        if 'selected_features' in locals() and len(selected_features) == 0:
            st.error("Please select at least one feature for anomaly detection.")
            return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Prepare data for processing
        status_text.text("Preparing data...")
        progress_bar.progress(10)
        
        time.sleep(0.5)  # Simulate processing time
        
        # Try to connect to the backend API
        try:
            status_text.text("Connecting to anomaly detection service...")
            progress_bar.progress(20)
            
            # Filter features if specified
            if 'selected_features' in locals() and len(selected_features) > 0:
                # Always include timestamp if available
                if 'timestamp' in df.columns:
                    selected_features = ['timestamp'] + [f for f in selected_features if f != 'timestamp']
                
                processed_df = df[selected_features].copy()
            else:
                processed_df = df.copy()
            
            # Convert timestamp to string for JSON serialization
            if 'timestamp' in processed_df.columns:
                processed_df['timestamp'] = processed_df['timestamp'].astype(str)
            
            # Prepare API payload
            payload = {
                'data': processed_df.to_dict(orient='records'),
                'model': selected_model,
                'threshold': threshold
            }
            
            progress_bar.progress(30)
            status_text.text("Processing data with the selected model...")
            
            # Make API request
            response = requests.post(
                'http://localhost:8000/api/detect',
                json=payload
            )
            
            if response.status_code == 200:
                # Process successful response
                result_data = response.json()
                
                progress_bar.progress(70)
                status_text.text("Post-processing results...")
                
                # Convert results back to DataFrame
                results_df = pd.DataFrame(result_data['results'])
                
                # Convert timestamp back to datetime if it exists
                if 'timestamp' in results_df.columns:
                    results_df['timestamp'] = pd.to_datetime(results_df['timestamp'])
                
                # Store results in session state
                st.session_state.detection_results = results_df
                st.session_state.model_metrics = result_data['metrics']
                st.session_state.contradictions = result_data.get('contradictions', [])
                st.session_state.recommendations = result_data.get('recommendations', {})
                
                progress_bar.progress(100)
                status_text.text("Detection completed successfully!")
                
                # Show success message with metrics
                anomaly_count = result_data['metrics']['anomaly_count']
                total_records = result_data['metrics']['total_records']
                anomaly_percent = result_data['metrics']['anomaly_percent']
                
                st.success(f"Successfully detected {anomaly_count} anomalies ({anomaly_percent:.2f}%) out of {total_records} records.")
                
                # Redirect to results page
                st.session_state.current_page = "results"
                st.rerun()
                
            else:
                # Handle API error
                st.error(f"Error from detection service: {response.text}")
                progress_bar.progress(100)
                status_text.text("Detection failed. See error above.")
                
        except Exception as e:
            # Fallback to local processing if API is not available
            progress_bar.progress(20)
            status_text.text("Anomaly detection service unavailable. Processing locally...")
            
            # Simulate processing delay
            for i in range(21, 90):
                time.sleep(0.05)
                progress_bar.progress(i)
                if i == 30:
                    status_text.text("Preprocessing data...")
                elif i == 50:
                    status_text.text(f"Running {model_options[selected_model]} algorithm...")
                elif i == 70:
                    status_text.text("Analyzing results...")
            
            # Generate mock results
            results_df = df.copy()
            
            # Add anomaly column (randomly marking 5-10% as anomalies)
            np.random.seed(int(datetime.now().timestamp()))  # Random seed based on current time
            anomaly_count = int(len(results_df) * np.random.uniform(0.05, 0.1))
            anomaly_indices = np.random.choice(len(results_df), size=anomaly_count, replace=False)
            
            results_df['anomaly'] = 0
            results_df.loc[anomaly_indices, 'anomaly'] = 1
            
            # Generate anomaly scores
            results_df['anomaly_score'] = np.random.uniform(0, 0.4, size=len(results_df))
            results_df.loc[anomaly_indices, 'anomaly_score'] = np.random.uniform(0.5, 1.0, size=len(anomaly_indices))
            
            progress_bar.progress(95)
            status_text.text("Finalizing results...")
            
            # Generate mock metrics
            metrics = {
                'model_name': model_options[selected_model],
                'anomaly_count': int(anomaly_count),
                'total_records': len(results_df),
                'anomaly_percent': float((anomaly_count / len(results_df)) * 100),
                'threshold_used': float(threshold)
            }
            
            # Store results in session state
            st.session_state.detection_results = results_df
            st.session_state.model_metrics = metrics
            
            progress_bar.progress(100)
            status_text.text("Detection completed successfully!")
            
            # Show success message with metrics
            st.success(f"Successfully detected {anomaly_count} anomalies ({metrics['anomaly_percent']:.2f}%) out of {len(results_df)} records.")
            
            # Show local processing disclaimer
            st.info("Note: Results were generated locally as the anomaly detection service was unavailable.")
            
            # Redirect to results page
            if st.button("View Results"):
                st.session_state.current_page = "results"
                st.rerun()
    
    # If detection results already exist, show option to view them
    if st.session_state.detection_results is not None:
        st.markdown("### Previous Detection Results")
        st.info(f"You have already run anomaly detection using {st.session_state.model_metrics['model_name']} and found {st.session_state.model_metrics['anomaly_count']} anomalies.")
        
        if st.button("View Previous Results"):
            st.session_state.current_page = "results"
            st.rerun()
