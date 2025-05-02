import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime

def show_dashboard():
    st.title("Energy Consumption Dashboard")
    
    # Check if data is available
    if st.session_state.uploaded_data is None:
        st.info("No data available. Please upload energy consumption data first.")
        return
    
    # Get data from session state
    df = st.session_state.uploaded_data
    
    # Create dashboard layout
    st.markdown("### Energy Consumption Overview")
    st.markdown("Interactive visualizations of your energy consumption patterns")
    
    # Create date filter if timestamp exists
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
        
        with col2:
            end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
        
        # Filter data based on date range
        mask = (df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)
        filtered_df = df[mask]
    else:
        filtered_df = df.copy()
    
    # Dashboard metrics
    metrics_cols = st.columns(4)
    
    # Metric 1: Total consumption
    if 'consumption' in filtered_df.columns:
        total_consumption = filtered_df['consumption'].sum()
        with metrics_cols[0]:
            st.metric("Total Consumption", f"{total_consumption:.2f} kWh")
    
    # Metric 2: Average consumption
    if 'consumption' in filtered_df.columns:
        avg_consumption = filtered_df['consumption'].mean()
        with metrics_cols[1]:
            st.metric("Avg. Consumption", f"{avg_consumption:.2f} kWh")
    
    # Metric 3: Peak consumption
    if 'consumption' in filtered_df.columns:
        peak_consumption = filtered_df['consumption'].max()
        with metrics_cols[2]:
            st.metric("Peak Consumption", f"{peak_consumption:.2f} kWh")
    
    # Metric 4: Data points
    with metrics_cols[3]:
        st.metric("Data Points", f"{len(filtered_df):,}")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Consumption Trends", "Distribution Analysis", "Pattern Insights"])
    
    with tab1:
        st.subheader("Energy Consumption Over Time")
        
        if 'timestamp' in filtered_df.columns and 'consumption' in filtered_df.columns:
            # Time series plot
            fig = px.line(
                filtered_df, 
                x='timestamp', 
                y='consumption',
                title='Energy Consumption Over Time',
                labels={'consumption': 'Consumption (kWh)', 'timestamp': 'Time'},
                template='plotly_dark'
            )
            
            # Add anomalies if available
            if 'anomaly' in filtered_df.columns and st.session_state.detection_results is not None:
                anomalies = filtered_df[filtered_df['anomaly'] == 1]
                
                fig.add_scatter(
                    x=anomalies['timestamp'],
                    y=anomalies['consumption'],
                    mode='markers',
                    marker=dict(color='red', size=10, symbol='circle'),
                    name='Anomalies'
                )
            
            fig.update_layout(
                height=500,
                xaxis_title='Time',
                yaxis_title='Consumption (kWh)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Daily/hourly heatmap
            if len(filtered_df) > 24:  # Only show if we have enough data
                st.subheader("Consumption Heatmap by Hour and Day")
                
                # Create hour of day feature if not already there
                if 'hour' not in filtered_df.columns:
                    filtered_df['hour'] = filtered_df['timestamp'].dt.hour
                
                # Create day of week feature if not already there
                if 'dayofweek' not in filtered_df.columns:
                    filtered_df['dayofweek'] = filtered_df['timestamp'].dt.dayofweek
                
                # Pivot data for heatmap
                pivot_df = filtered_df.pivot_table(
                    index='hour',
                    columns='dayofweek',
                    values='consumption',
                    aggfunc='mean'
                ).fillna(0)
                
                # Create heatmap
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                fig = px.imshow(
                    pivot_df,
                    labels=dict(x="Day of Week", y="Hour of Day", color="Consumption"),
                    x=day_names,
                    y=list(range(24)),
                    color_continuous_scale='Viridis',
                    template='plotly_dark'
                )
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Timestamp or consumption data not available for time series visualization.")
    
    with tab2:
        st.subheader("Consumption Distribution Analysis")
        
        if 'consumption' in filtered_df.columns:
            # Distribution plot
            col1, col2 = st.columns(2)
            
            with col1:
                # Histogram
                fig = px.histogram(
                    filtered_df,
                    x='consumption',
                    nbins=30,
                    marginal='box',
                    title='Consumption Distribution',
                    template='plotly_dark',
                    color_discrete_sequence=['#636EFA']
                )
                
                fig.update_layout(
                    xaxis_title='Consumption (kWh)',
                    yaxis_title='Frequency',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Box plot by location if available
                if 'location' in filtered_df.columns:
                    fig = px.box(
                        filtered_df,
                        x='location',
                        y='consumption',
                        color='location',
                        title='Consumption by Location',
                        template='plotly_dark'
                    )
                    
                    fig.update_layout(
                        xaxis_title='Location',
                        yaxis_title='Consumption (kWh)',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Box plot by time of day if available
                    if 'time_of_day' in filtered_df.columns:
                        fig = px.box(
                            filtered_df,
                            x='time_of_day',
                            y='consumption',
                            color='time_of_day',
                            title='Consumption by Time of Day',
                            template='plotly_dark',
                            category_orders={'time_of_day': ['morning', 'afternoon', 'evening', 'night']}
                        )
                        
                        fig.update_layout(
                            xaxis_title='Time of Day',
                            yaxis_title='Consumption (kWh)',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Simple violin plot
                        fig = px.violin(
                            filtered_df,
                            y='consumption',
                            box=True,
                            points="all",
                            title='Consumption Distribution',
                            template='plotly_dark'
                        )
                        
                        fig.update_layout(
                            yaxis_title='Consumption (kWh)',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            
            # Anomaly score distribution if available
            if 'anomaly_score' in filtered_df.columns and st.session_state.detection_results is not None:
                st.subheader("Anomaly Score Distribution")
                
                fig = px.histogram(
                    filtered_df,
                    x='anomaly_score',
                    nbins=30,
                    marginal='box',
                    title='Anomaly Score Distribution',
                    template='plotly_dark',
                    color_discrete_sequence=['#EF553B']
                )
                
                # Add threshold line if available
                if hasattr(st.session_state, 'anomaly_threshold'):
                    fig.add_vline(
                        x=st.session_state.anomaly_threshold,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Threshold: {st.session_state.anomaly_threshold:.2f}",
                        annotation_position="top right"
                    )
                
                fig.update_layout(
                    xaxis_title='Anomaly Score',
                    yaxis_title='Frequency',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Consumption data not available for distribution analysis.")
    
    with tab3:
        st.subheader("Energy Consumption Patterns")
        
        # Temperature vs. consumption
        if 'temperature' in filtered_df.columns and 'consumption' in filtered_df.columns:
            st.markdown("#### Temperature vs. Consumption")
            
            fig = px.scatter(
                filtered_df,
                x='temperature',
                y='consumption',
                trendline='ols',
                title='Temperature vs. Consumption Relationship',
                template='plotly_dark',
                opacity=0.7
            )
            
            # Add anomalies if available
            if 'anomaly' in filtered_df.columns and st.session_state.detection_results is not None:
                anomalies = filtered_df[filtered_df['anomaly'] == 1]
                
                fig.add_scatter(
                    x=anomalies['temperature'],
                    y=anomalies['consumption'],
                    mode='markers',
                    marker=dict(color='red', size=10, symbol='circle'),
                    name='Anomalies'
                )
            
            fig.update_layout(
                xaxis_title='Temperature',
                yaxis_title='Consumption (kWh)',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Consumption by hour of day
        if 'hour' in filtered_df.columns and 'consumption' in filtered_df.columns:
            st.markdown("#### Consumption by Hour of Day")
            
            hourly_avg = filtered_df.groupby('hour')['consumption'].mean().reset_index()
            
            fig = px.bar(
                hourly_avg,
                x='hour',
                y='consumption',
                title='Average Consumption by Hour of Day',
                template='plotly_dark',
                color='consumption',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                xaxis_title='Hour of Day',
                yaxis_title='Average Consumption (kWh)',
                xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Consumption by day of week if available
        if 'dayofweek' in filtered_df.columns and 'consumption' in filtered_df.columns:
            st.markdown("#### Consumption by Day of Week")
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_avg = filtered_df.groupby('dayofweek')['consumption'].mean().reset_index()
            daily_avg['day_name'] = daily_avg['dayofweek'].apply(lambda x: day_names[x])
            
            fig = px.bar(
                daily_avg,
                x='day_name',
                y='consumption',
                title='Average Consumption by Day of Week',
                template='plotly_dark',
                color='consumption',
                color_continuous_scale='Viridis',
                category_orders={'day_name': day_names}
            )
            
            fig.update_layout(
                xaxis_title='Day of Week',
                yaxis_title='Average Consumption (kWh)',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
