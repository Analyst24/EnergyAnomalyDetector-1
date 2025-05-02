import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

def show_model_insights():
    st.title("Model Insights")
    
    # Check if detection results are available
    if st.session_state.detection_results is None or st.session_state.model_metrics is None:
        st.info("No detection results available. Please run anomaly detection first.")
        if st.button("Go to Detection Page"):
            st.session_state.current_page = "detection"
            st.rerun()
        return
    
    # Get results and metrics from session state
    results = st.session_state.detection_results
    metrics = st.session_state.model_metrics
    
    # Display model overview
    st.markdown(f"### Model: {metrics['model_name']}")
    
    # Create metrics display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Anomalies Detected", metrics['anomaly_count'])
    
    with col2:
        st.metric("Anomaly Percentage", f"{metrics['anomaly_percent']:.2f}%")
    
    with col3:
        st.metric("Threshold Used", f"{metrics['threshold_used']:.2f}")
    
    # Create tabs for different insights
    tab1, tab2 = st.tabs(["Performance Analysis", "Feature Importance"])
    
    with tab1:
        st.markdown("### Model Performance")
        
        # Create confusion matrix-like visualization (even though we don't have true labels)
        # This is a visualization of prediction distribution
        anomaly_count = metrics['anomaly_count']
        normal_count = metrics['total_records'] - anomaly_count
        
        # Create a Figure
        fig = go.Figure()
        
        # Define the matrix
        matrix = [[normal_count, 0], [0, anomaly_count]]
        
        # Create heatmap
        heatmap = go.Heatmap(
            z=matrix,
            x=['Normal', 'Anomaly'],
            y=['Normal', 'Anomaly'],
            text=[[str(normal_count), '0'], ['0', str(anomaly_count)]],
            texttemplate="%{text}",
            colorscale='Viridis'
        )
        
        fig.add_trace(heatmap)
        
        fig.update_layout(
            title="Prediction Distribution",
            height=400,
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show anomaly score distribution
        if 'anomaly_score' in results.columns:
            st.markdown("### Anomaly Score Distribution")
            
            # Split data into normal and anomalous points
            normal_points = results[results['anomaly'] == 0]
            anomalous_points = results[results['anomaly'] == 1]
            
            # Create histogram of anomaly scores
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=normal_points['anomaly_score'],
                name='Normal',
                marker_color='blue',
                opacity=0.6,
                nbinsx=30
            ))
            
            fig.add_trace(go.Histogram(
                x=anomalous_points['anomaly_score'],
                name='Anomaly',
                marker_color='red',
                opacity=0.6,
                nbinsx=30
            ))
            
            # Add threshold line
            fig.add_vline(
                x=metrics['threshold_used'],
                line_dash="dash",
                line_color="green",
                annotation_text=f"Threshold: {metrics['threshold_used']:.2f}",
                annotation_position="top right"
            )
            
            fig.update_layout(
                title="Distribution of Anomaly Scores",
                xaxis_title='Anomaly Score',
                yaxis_title='Count',
                barmode='overlay',
                height=400,
                template='plotly_dark'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Additional model-specific metrics
        if metrics['model_name'] == 'K-Means Clustering' and 'cluster_distribution' in metrics:
            st.markdown("### Cluster Distribution")
            
            # Extract cluster distribution
            clusters = []
            counts = []
            percentages = []
            
            for cluster, data in metrics['cluster_distribution'].items():
                clusters.append(cluster)
                counts.append(data['count'])
                percentages.append(data['percent'])
            
            # Create DataFrame
            cluster_df = pd.DataFrame({
                'Cluster': clusters,
                'Count': counts,
                'Percentage': percentages
            })
            
            # Create bar chart
            fig = px.bar(
                cluster_df,
                x='Cluster',
                y='Count',
                text='Percentage',
                title='Distribution of Data Points Across Clusters',
                template='plotly_dark',
                color='Count'
            )
            
            fig.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            
            fig.update_layout(
                xaxis_title='Cluster',
                yaxis_title='Number of Data Points',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        elif metrics['model_name'] == 'Autoencoder' and 'training_loss' in metrics:
            st.markdown("### Autoencoder Training Performance")
            
            # Create gauge for training loss
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['training_loss'],
                title={'text': "Training Loss"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, max(metrics['training_loss'] * 2, 0.01)]},
                    'bar': {'color': "blue"},
                    'steps': [
                        {'range': [0, metrics['training_loss'] / 2], 'color': "green"},
                        {'range': [metrics['training_loss'] / 2, metrics['training_loss']], 'color': "yellow"},
                        {'range': [metrics['training_loss'], metrics['training_loss'] * 2], 'color': "red"}
                    ]
                }
            ))
            
            fig.update_layout(
                height=300,
                template='plotly_dark'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # If validation loss is available
            if 'validation_loss' in metrics and metrics['validation_loss'] is not None:
                # Compare training and validation loss
                train_val_df = pd.DataFrame({
                    'Metric': ['Training Loss', 'Validation Loss'],
                    'Value': [metrics['training_loss'], metrics['validation_loss']]
                })
                
                fig = px.bar(
                    train_val_df,
                    x='Metric',
                    y='Value',
                    title='Training vs. Validation Loss',
                    template='plotly_dark',
                    color='Metric'
                )
                
                fig.update_layout(
                    height=400,
                    yaxis_title='Loss Value'
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Feature Importance Analysis")
        
        # Get numerical columns from results
        numerical_cols = results.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        # Remove anomaly-related columns
        feature_cols = [col for col in numerical_cols if col not in ['anomaly', 'anomaly_score']]
        
        if len(feature_cols) > 0:
            # Calculate correlation between features and anomaly score
            feature_importance = {}
            
            for col in feature_cols:
                if 'anomaly_score' in results.columns:
                    corr = abs(results[col].corr(results['anomaly_score']))
                    feature_importance[col] = corr
            
            # Create DataFrame for visualization
            importance_df = pd.DataFrame({
                'Feature': list(feature_importance.keys()),
                'Importance': list(feature_importance.values())
            }).sort_values('Importance', ascending=False)
            
            # Create bar chart
            fig = px.bar(
                importance_df,
                x='Feature',
                y='Importance',
                title='Feature Importance (Correlation with Anomaly Score)',
                template='plotly_dark',
                color='Importance'
            )
            
            fig.update_layout(
                xaxis_title='Feature',
                yaxis_title='Absolute Correlation',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show scatter plots for top 2 features vs anomaly score
            if len(importance_df) >= 2:
                st.markdown("### Top Feature Relationships")
                
                top_features = importance_df.head(2)['Feature'].tolist()
                
                col1, col2 = st.columns(2)
                
                for i, feature in enumerate(top_features):
                    fig = px.scatter(
                        results,
                        x=feature,
                        y='anomaly_score',
                        color='anomaly',
                        title=f"{feature} vs. Anomaly Score",
                        template='plotly_dark',
                        color_discrete_map={0: 'blue', 1: 'red'}
                    )
                    
                    fig.update_layout(
                        xaxis_title=feature,
                        yaxis_title='Anomaly Score',
                        height=400,
                        legend=dict(
                            title="Anomaly",
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01,
                            orientation="h"
                        )
                    )
                    
                    # Add to the appropriate column
                    if i == 0:
                        with col1:
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        with col2:
                            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No numerical features available for importance analysis.")
    
    # Download section
    st.markdown("### Download Model Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Performance Report"):
            # Generate performance report
            buffer = BytesIO()
            plt.figure(figsize=(10, 6))
            
            # Create a PDF-like report using BytesIO
            report_text = f"""
            ## Anomaly Detection Model Performance Report
            
            ### Model: {metrics['model_name']}
            
            #### Key Metrics:
            - Anomalies Detected: {metrics['anomaly_count']}
            - Total Records: {metrics['total_records']}
            - Anomaly Percentage: {metrics['anomaly_percent']:.2f}%
            - Threshold Used: {metrics['threshold_used']:.2f}
            
            This report was generated automatically by the Energy Efficiency Anomaly Detection System.
            """
            
            st.download_button(
                label="Download Performance Report",
                data=report_text,
                file_name="anomaly_detection_report.md",
                mime="text/markdown"
            )
    
    with col2:
        if st.button("Download Model Configuration"):
            # Generate model configuration
            config_text = f"""
            ## Anomaly Detection Model Configuration
            
            ### Model: {metrics['model_name']}
            
            #### Parameters:
            - Threshold: {metrics['threshold_used']:.2f}
            
            Additional parameters depend on the specific model used.
            
            This configuration was used to detect {metrics['anomaly_count']} anomalies out of {metrics['total_records']} total records.
            """
            
            st.download_button(
                label="Download Model Configuration",
                data=config_text,
                file_name="model_configuration.md",
                mime="text/markdown"
            )
