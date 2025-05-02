import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import io
import base64
import json
import matplotlib.pyplot as plt

def show_results_page():
    st.title("Anomaly Detection Results")
    
    # Check if detection results are available
    if st.session_state.detection_results is None:
        st.info("No detection results available. Please run anomaly detection first.")
        if st.button("Go to Detection Page"):
            st.session_state.current_page = "detection"
            st.rerun()
        return
    
    # Get results and metrics from session state
    results = st.session_state.detection_results
    metrics = st.session_state.model_metrics
    
    # Create summary section
    st.markdown("### Summary of Detection Results")
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model Used", metrics['model_name'])
    
    with col2:
        st.metric("Anomalies Found", metrics['anomaly_count'])
    
    with col3:
        st.metric("Total Records", metrics['total_records'])
    
    with col4:
        st.metric("Anomaly Rate", f"{metrics['anomaly_percent']:.2f}%")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Anomaly Overview", "Detailed Analysis", "Data Explorer"])
    
    with tab1:
        st.markdown("### Anomaly Distribution Overview")
        
        # Create anomaly time series if timestamp is present
        if 'timestamp' in results.columns and 'consumption' in results.columns:
            # Create time series plot with anomalies highlighted
            fig = px.line(
                results,
                x='timestamp',
                y='consumption',
                title='Energy Consumption with Detected Anomalies',
                template='plotly_dark'
            )
            
            # Add anomalies
            anomalies = results[results['anomaly'] == 1]
            
            fig.add_scatter(
                x=anomalies['timestamp'],
                y=anomalies['consumption'],
                mode='markers',
                marker=dict(color='red', size=10, symbol='circle'),
                name='Anomalies'
            )
            
            fig.update_layout(
                xaxis_title='Time',
                yaxis_title='Energy Consumption',
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create heatmap of anomalies by hour and day if those columns exist
            if all(col in results.columns for col in ['hour', 'dayofweek']):
                st.markdown("### Anomaly Heatmap by Hour and Day")
                
                # Count anomalies by hour and day
                anomaly_counts = anomalies.groupby(['dayofweek', 'hour']).size().reset_index(name='count')
                
                # Create a pivot table
                pivot_anomalies = anomaly_counts.pivot(index='hour', columns='dayofweek', values='count').fillna(0)
                
                # Create heatmap
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                
                fig = px.imshow(
                    pivot_anomalies,
                    labels=dict(x="Day of Week", y="Hour of Day", color="Anomaly Count"),
                    x=day_names[:pivot_anomalies.shape[1]],  # Use only the days we have
                    y=list(range(24)),
                    color_continuous_scale='Reds',
                    template='plotly_dark'
                )
                
                fig.update_layout(
                    title='Anomaly Distribution by Hour and Day',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # If no timestamp but we have location, show anomalies by location
        elif 'location' in results.columns:
            # Count anomalies by location
            location_counts = results[results['anomaly'] == 1].groupby('location').size().reset_index(name='count')
            total_by_location = results.groupby('location').size().reset_index(name='total')
            
            # Merge to get percentages
            location_stats = pd.merge(location_counts, total_by_location, on='location')
            location_stats['percentage'] = (location_stats['count'] / location_stats['total']) * 100
            
            # Create bar chart
            fig = px.bar(
                location_stats,
                x='location',
                y='count',
                color='percentage',
                title='Anomalies by Location',
                template='plotly_dark',
                color_continuous_scale='Reds',
                labels={'count': 'Number of Anomalies', 'location': 'Location', 'percentage': 'Anomaly %'}
            )
            
            fig.update_layout(
                xaxis_title='Location',
                yaxis_title='Number of Anomalies',
                height=500
            )
            
            # Add percentage labels
            fig.update_traces(texttemplate='%{y} (%{marker.color:.1f}%)', textposition='outside')
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Detailed Anomaly Analysis")
        
        # Create scatter plot of consumption vs other relevant features
        # Select features for analysis
        numerical_cols = results.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        # Remove non-feature columns
        exclude_cols = ['anomaly', 'anomaly_score']
        feature_cols = [col for col in numerical_cols if col not in exclude_cols]
        
        if len(feature_cols) >= 2:
            # Let user select features to compare
            if 'consumption' in feature_cols:
                default_y = 'consumption'
                feature_cols.remove('consumption')
            else:
                default_y = feature_cols[0]
                feature_cols.remove(default_y)
            
            default_x = feature_cols[0] if feature_cols else None
            
            if default_x:
                col1, col2 = st.columns(2)
                
                with col1:
                    x_feature = st.selectbox(
                        "Select X-axis feature:",
                        options=feature_cols,
                        index=0
                    )
                
                with col2:
                    available_y = [col for col in numerical_cols if col != x_feature and col not in exclude_cols]
                    y_feature = st.selectbox(
                        "Select Y-axis feature:",
                        options=available_y,
                        index=available_y.index(default_y) if default_y in available_y else 0
                    )
                
                # Create scatter plot
                fig = px.scatter(
                    results,
                    x=x_feature,
                    y=y_feature,
                    color='anomaly',
                    color_discrete_map={0: 'blue', 1: 'red'},
                    title=f'{y_feature} vs {x_feature} with Anomalies Highlighted',
                    template='plotly_dark',
                    size='anomaly_score' if 'anomaly_score' in results.columns else None,
                    size_max=15,
                    hover_data=['anomaly_score'] if 'anomaly_score' in results.columns else None
                )
                
                fig.update_layout(
                    xaxis_title=x_feature,
                    yaxis_title=y_feature,
                    height=600,
                    legend=dict(
                        title="Anomaly",
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01,
                        orientation="h"
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough numerical features available for detailed analysis.")
        else:
            st.info("Not enough numerical features available for detailed analysis.")
        
        # If we have time features, show distribution of anomalies by time
        if 'hour' in results.columns:
            st.markdown("### Anomaly Distribution by Time of Day")
            
            # Count anomalies by hour
            hour_counts = results[results['anomaly'] == 1].groupby('hour').size().reset_index(name='anomaly_count')
            total_by_hour = results.groupby('hour').size().reset_index(name='total_count')
            
            # Merge to get percentages
            hour_stats = pd.merge(hour_counts, total_by_hour, on='hour')
            hour_stats['percentage'] = (hour_stats['anomaly_count'] / hour_stats['total_count']) * 100
            
            # Create bar chart
            fig = px.bar(
                hour_stats,
                x='hour',
                y='anomaly_count',
                color='percentage',
                title='Anomalies by Hour of Day',
                template='plotly_dark',
                color_continuous_scale='Reds',
                labels={'anomaly_count': 'Number of Anomalies', 'hour': 'Hour of Day', 'percentage': 'Anomaly %'}
            )
            
            fig.update_layout(
                xaxis_title='Hour of Day',
                yaxis_title='Number of Anomalies',
                height=400,
                xaxis=dict(tickmode='linear', tick0=0, dtick=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # If we have temperature, show relationship between temperature and anomalies
        if 'temperature' in results.columns and 'consumption' in results.columns:
            st.markdown("### Temperature vs Consumption Analysis")
            
            # Try to create scatter plot with trendline, but handle case where statsmodels isn't available
            try:
                fig = px.scatter(
                    results,
                    x='temperature',
                    y='consumption',
                    color='anomaly',
                    color_discrete_map={0: 'blue', 1: 'red'},
                    title='Temperature vs Consumption with Anomalies Highlighted',
                    template='plotly_dark',
                    trendline='ols',
                    trendline_scope='overall'
                )
            except ImportError:
                # Fallback to basic scatter plot without trendline if statsmodels isn't available
                fig = px.scatter(
                    results,
                    x='temperature',
                    y='consumption',
                    color='anomaly',
                    color_discrete_map={0: 'blue', 1: 'red'},
                    title='Temperature vs Consumption with Anomalies Highlighted (no trendline)',
                    template='plotly_dark'
                )
            
            fig.update_layout(
                xaxis_title='Temperature',
                yaxis_title='Consumption',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Explore Anomaly Data")
        
        # Add a filter for viewing all data or just anomalies
        data_view = st.radio(
            "Select data to view:",
            ["All Data", "Anomalies Only", "Normal Data Only"],
            horizontal=True
        )
        
        # Apply filter based on selection
        if data_view == "Anomalies Only":
            display_df = results[results['anomaly'] == 1]
            st.markdown(f"Showing {len(display_df)} anomalous records")
        elif data_view == "Normal Data Only":
            display_df = results[results['anomaly'] == 0]
            st.markdown(f"Showing {len(display_df)} normal records")
        else:
            display_df = results
            st.markdown(f"Showing all {len(display_df)} records")
        
        # Show data table with sorting and filtering
        st.dataframe(display_df, use_container_width=True)
        
        # Add download options
        st.markdown("### Download Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name="anomaly_detection_results.csv",
                mime="text/csv"
            )
        
        with col2:
            # Create a PDF-like report (as markdown since we can't generate PDFs directly)
            report_text = f"""
            # Anomaly Detection Report
            
            ## Summary
            - **Model Used**: {metrics['model_name']}
            - **Anomalies Found**: {metrics['anomaly_count']}
            - **Total Records**: {metrics['total_records']}
            - **Anomaly Rate**: {metrics['anomaly_percent']:.2f}%
            - **Threshold Used**: {metrics['threshold_used']}
            
            ## Detection Details
            This report contains detailed information about anomalies detected in energy consumption data.
            
            ## Top Anomalies
            """
            
            # Add top 5 anomalies if anomaly score exists
            if 'anomaly_score' in results.columns:
                top_anomalies = results[results['anomaly'] == 1].nlargest(5, 'anomaly_score')
                for i, (idx, row) in enumerate(top_anomalies.iterrows()):
                    report_text += f"\n### Anomaly {i+1}\n"
                    report_text += f"- **Score**: {row['anomaly_score']:.4f}\n"
                    
                    # Add timestamp if exists
                    if 'timestamp' in row:
                        report_text += f"- **Time**: {row['timestamp']}\n"
                    
                    # Add consumption if exists
                    if 'consumption' in row:
                        report_text += f"- **Consumption**: {row['consumption']:.2f}\n"
                    
                    # Add other relevant columns
                    for col in row.index:
                        if col not in ['anomaly', 'anomaly_score', 'timestamp', 'consumption']:
                            report_text += f"- **{col}**: {row[col]}\n"
            
            report_text += "\n\n© 2025 Opulent Chikwiramakomo. All rights reserved."
            
            st.download_button(
                label="Download Report",
                data=report_text,
                file_name="anomaly_detection_report.md",
                mime="text/markdown"
            )
    
    # Show contradictions section if available
    if hasattr(st.session_state, 'contradictions') and st.session_state.contradictions:
        st.markdown("### Data Contradictions Detected")
        
        contradictions = st.session_state.contradictions
        
        for i, contradiction in enumerate(contradictions):
            with st.expander(f"{contradiction['message']} ({contradiction['count']} instances)"):
                st.markdown(f"**Type**: {contradiction['type']}")
                st.markdown(f"**Count**: {contradiction['count']}")
                st.markdown("**Details**: These contradictions may indicate data quality issues or genuine anomalies that require special attention.")
    
    # Footer
    st.markdown("---")
    st.markdown("Navigate to the **Model Insights** page for more detailed analysis of the model performance, or to the **Recommendations** page for actionable insights.")
