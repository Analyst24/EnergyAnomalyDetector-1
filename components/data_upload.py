import streamlit as st
import pandas as pd
import io
import plotly.express as px
import numpy as np

def show_data_upload():
    st.title("Upload Energy Consumption Data")
    
    st.markdown("""
    ### Upload your energy consumption CSV file
    
    Your file should contain columns such as:
    * timestamp
    * consumption
    * meter_id (optional)
    * location (optional)
    * temperature (optional)
    * humidity (optional)
    * season / time_of_day (optional)
    """)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Basic validation
            if len(df) == 0:
                st.error("The uploaded file is empty.")
                return
            
            # Check for required columns
            required_cols = ['consumption']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"The following required columns are missing: {', '.join(missing_cols)}")
                st.markdown("Please ensure your CSV file contains at least the 'consumption' column.")
                return
            
            # Convert timestamp to datetime if it exists
            if 'timestamp' in df.columns:
                try:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                except:
                    st.warning("Could not convert 'timestamp' column to datetime format. Treating it as string.")
            
            # Show success message
            st.success(f"File successfully uploaded: {len(df)} rows and {len(df.columns)} columns")
            
            # Display sample data
            st.subheader("Sample Data")
            st.dataframe(df.head(10))
            
            # Data quality check
            st.subheader("Data Quality Check")
            
            # Check for missing values
            missing_values = df.isnull().sum()
            missing_percent = (missing_values / len(df)) * 100
            
            missing_df = pd.DataFrame({
                'Column': missing_values.index,
                'Missing Values': missing_values.values,
                'Missing Percent': missing_percent.values
            })
            
            # Show columns with missing values
            missing_df = missing_df[missing_df['Missing Values'] > 0].sort_values('Missing Values', ascending=False)
            
            if len(missing_df) > 0:
                st.markdown("#### Missing Values")
                st.dataframe(missing_df)
                
                # Provide option to handle missing values
                st.markdown("#### Handle Missing Values")
                
                handling_method = st.selectbox(
                    "Choose a method to handle missing values:",
                    ["Drop rows with any missing values", 
                     "Fill numeric missing values with mean",
                     "Fill numeric missing values with median", 
                     "Leave as is (handle during analysis)"]
                )
                
                if st.button("Apply Missing Value Handling"):
                    if handling_method == "Drop rows with any missing values":
                        df = df.dropna()
                        st.info(f"Dropped rows with missing values. {len(df)} rows remaining.")
                    
                    elif handling_method == "Fill numeric missing values with mean":
                        for col in df.select_dtypes(include=['float64', 'int64']).columns:
                            if df[col].isnull().sum() > 0:
                                df[col] = df[col].fillna(df[col].mean())
                        
                        st.info("Filled numeric missing values with column means.")
                    
                    elif handling_method == "Fill numeric missing values with median":
                        for col in df.select_dtypes(include=['float64', 'int64']).columns:
                            if df[col].isnull().sum() > 0:
                                df[col] = df[col].fillna(df[col].median())
                        
                        st.info("Filled numeric missing values with column medians.")
                    
                    else:
                        st.info("Keeping missing values as is.")
            else:
                st.success("No missing values found in the dataset!")
            
            # Data visualization
            st.subheader("Data Overview")
            
            # Consumption overview
            if 'consumption' in df.columns:
                st.markdown("#### Consumption Distribution")
                
                fig = px.histogram(
                    df, 
                    x='consumption',
                    nbins=30,
                    title='Distribution of Consumption Values',
                    template='plotly_dark'
                )
                
                st.plotly_chart(fig)
            
            # Time series overview if timestamp exists
            if 'timestamp' in df.columns and 'consumption' in df.columns:
                st.markdown("#### Consumption Over Time")
                
                # Sample the data if it's too large
                if len(df) > 1000:
                    sample_size = min(1000, int(len(df) * 0.1))
                    plot_df = df.sample(sample_size)
                else:
                    plot_df = df
                
                fig = px.line(
                    plot_df.sort_values('timestamp'),
                    x='timestamp',
                    y='consumption',
                    title='Consumption Over Time (Sample)',
                    template='plotly_dark'
                )
                
                st.plotly_chart(fig)
            
            # Check for contradictions or potential data issues
            st.subheader("Data Consistency Check")
            
            issues_found = False
            
            # Check for negative consumption values
            if 'consumption' in df.columns:
                neg_consumption = df[df['consumption'] < 0]
                if len(neg_consumption) > 0:
                    st.warning(f"Found {len(neg_consumption)} records with negative consumption values.")
                    issues_found = True
            
            # Check for extreme values (potential outliers)
            if 'consumption' in df.columns:
                q1 = df['consumption'].quantile(0.25)
                q3 = df['consumption'].quantile(0.75)
                iqr = q3 - q1
                
                outliers = df[(df['consumption'] < q1 - 1.5 * iqr) | (df['consumption'] > q3 + 1.5 * iqr)]
                
                if len(outliers) > 0:
                    outlier_percent = (len(outliers) / len(df)) * 100
                    st.warning(f"Found {len(outliers)} potential outliers ({outlier_percent:.2f}% of data) in consumption values.")
                    issues_found = True
            
            # Check for duplicated timestamps if timestamp exists
            if 'timestamp' in df.columns:
                duplicates = df[df.duplicated('timestamp', keep=False)]
                
                if len(duplicates) > 0:
                    st.warning(f"Found {len(duplicates)} records with duplicate timestamps.")
                    issues_found = True
            
            if not issues_found:
                st.success("No major data inconsistencies detected!")
            
            # Save data to session state
            if st.button("Confirm and Save Data"):
                st.session_state.uploaded_data = df
                st.success("Data saved successfully! You can now proceed to the Detection page.")
                
                # Add recommendation to go to the detection page
                st.info("Navigate to the 'Run Detection' page to analyze this data for anomalies.")
                
        except Exception as e:
            st.error(f"Error processing the uploaded file: {str(e)}")
    else:
        # Show sample dataset option
        st.markdown("### Or use a sample dataset")
        if st.button("Load Sample Energy Data"):
            # Load sample data
            try:
                sample_df = pd.read_csv('data/sample_energy_data.csv')
                
                if 'timestamp' in sample_df.columns:
                    sample_df['timestamp'] = pd.to_datetime(sample_df['timestamp'])
                
                st.session_state.uploaded_data = sample_df
                st.success("Sample data loaded successfully!")
                
                # Display sample data preview
                st.subheader("Sample Data Preview")
                st.dataframe(sample_df.head(10))
                
                # Add recommendation to go to the detection page
                st.info("Navigate to the 'Run Detection' page to analyze this data for anomalies.")
                
            except Exception as e:
                st.error(f"Error loading sample data: {str(e)}")
                
                # Generate a simple synthetic sample if real sample is not available
                st.warning("Generating a simple synthetic sample instead.")
                
                # Create date range for the last 30 days
                dates = pd.date_range(end=pd.Timestamp.now(), periods=720, freq='H')
                
                # Create synthetic data
                np.random.seed(42)  # For reproducibility
                consumption = np.random.normal(loc=100, scale=20, size=len(dates))
                
                # Add daily and weekly patterns
                hour_effect = np.sin(np.pi * dates.hour / 12) * 30
                weekday_effect = np.where(dates.dayofweek < 5, 20, -20)
                
                consumption = consumption + hour_effect + weekday_effect
                
                # Add temperature data
                temperature = np.random.normal(loc=25, scale=5, size=len(dates))
                
                # Create location data
                locations = np.random.choice(['residential', 'commercial', 'industrial'], size=len(dates))
                
                # Create meter IDs
                meter_ids = np.random.choice(['meter001', 'meter002', 'meter003', 'meter004'], size=len(dates))
                
                # Create DataFrame
                sample_df = pd.DataFrame({
                    'timestamp': dates,
                    'consumption': consumption,
                    'temperature': temperature,
                    'location': locations,
                    'meter_id': meter_ids
                })
                
                # Add a few anomalies (5% of data)
                anomaly_indices = np.random.choice(len(sample_df), size=int(0.05 * len(sample_df)), replace=False)
                sample_df.loc[anomaly_indices, 'consumption'] = sample_df.loc[anomaly_indices, 'consumption'] * np.random.uniform(1.5, 3, size=len(anomaly_indices))
                
                st.session_state.uploaded_data = sample_df
                st.success("Synthetic sample data generated and loaded successfully!")
                
                # Display sample data preview
                st.subheader("Synthetic Sample Data Preview")
                st.dataframe(sample_df.head(10))
                
                # Save the synthetic sample
                try:
                    if not os.path.exists('data'):
                        os.makedirs('data')
                    sample_df.to_csv('data/sample_energy_data.csv', index=False)
                except:
                    st.warning("Could not save the synthetic sample to file.")
