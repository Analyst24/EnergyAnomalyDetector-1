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
    tab1, tab2, tab3 = st.tabs(["Performance Analysis", "Evaluation Metrics", "Feature Importance"])
    
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
        st.markdown("### Model Evaluation Metrics")
        
        # Check if evaluation metrics are available
        if 'accuracy' in metrics and 'precision' in metrics and 'recall' in metrics and 'f1_score' in metrics:
            # Create metrics cards
            st.markdown("""
            <style>
            .metric-card {
                background-color: rgba(30, 33, 48, 0.9);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .metric-title {
                font-size: 1.2em;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .metric-value {
                font-size: 2.2em;
                font-weight: bold;
                color: #4CAF50;
                margin: 5px 0;
            }
            .metric-description {
                font-size: 0.9em;
                color: #cccccc;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create 4 metric columns
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Accuracy</div>
                    <div class="metric-value">{metrics['accuracy']:.2f}</div>
                    <div class="metric-description">
                        Overall correctness of predictions. Ratio of correctly identified samples to total samples.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Precision</div>
                    <div class="metric-value">{metrics['precision']:.2f}</div>
                    <div class="metric-description">
                        Ratio of correctly identified anomalies to all predicted anomalies. Measures false alarm rate.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">Recall</div>
                    <div class="metric-value">{metrics['recall']:.2f}</div>
                    <div class="metric-description">
                        Ratio of correctly identified anomalies to all actual anomalies. Measures detection rate.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">F1 Score</div>
                    <div class="metric-value">{metrics['f1_score']:.2f}</div>
                    <div class="metric-description">
                        Harmonic mean of precision and recall. Balanced measure of model performance.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Add confusion matrix visualization
            st.markdown("### Confusion Matrix")
            
            matrix_values = [
                [metrics['true_negatives'], metrics['false_positives']],
                [metrics['false_negatives'], metrics['true_positives']]
            ]
            
            fig = go.Figure(data=go.Heatmap(
                z=matrix_values,
                x=['Predicted Normal', 'Predicted Anomaly'],
                y=['Actual Normal', 'Actual Anomaly'],
                text=[[str(metrics['true_negatives']), str(metrics['false_positives'])],
                      [str(metrics['false_negatives']), str(metrics['true_positives'])]],
                texttemplate="%{text}",
                colorscale='Blues'
            ))
            
            fig.update_layout(
                title="Confusion Matrix",
                height=500,
                template='plotly_dark'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation
            st.markdown("""
            ### Metric Definitions:
            
            - **True Positives (TP)**: Anomalies correctly identified as anomalies
            - **False Positives (FP)**: Normal points incorrectly identified as anomalies
            - **True Negatives (TN)**: Normal points correctly identified as normal
            - **False Negatives (FN)**: Anomalies incorrectly identified as normal
            
            ### Model Comparison
            
            Different models may excel at different aspects of anomaly detection:
            
            - **Isolation Forest** typically provides good overall performance and is efficient for large datasets
            - **Autoencoder** can capture complex patterns and non-linear relationships in the data
            - **K-Means Clustering** is useful for identifying distinct groups of anomalies
            """)
            
            # Show ROC curve-like visualization
            st.markdown("### Performance Trade-off Visualization")
            
            # Create a scatter plot with performance metrics
            metrics_df = pd.DataFrame({
                'Metric': ['Precision', 'Recall', 'Accuracy', 'F1 Score'],
                'Value': [metrics['precision'], metrics['recall'], metrics['accuracy'], metrics['f1_score']]
            })
            
            fig = px.bar(
                metrics_df,
                x='Metric',
                y='Value',
                color='Value',
                color_continuous_scale='Viridis',
                title=f"Performance Metrics for {metrics['model_name']}",
                template='plotly_dark'
            )
            
            fig.update_layout(
                xaxis_title='Metric',
                yaxis_title='Value (0-1 scale)',
                height=400,
                yaxis=dict(range=[0, 1])
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Evaluation metrics are not available for this model run. Run detection again to see evaluation metrics.")
    
    with tab3:
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
            # Add evaluation metrics to report if available
            eval_metrics_text = ""
            if 'accuracy' in metrics and 'precision' in metrics and 'recall' in metrics and 'f1_score' in metrics:
                eval_metrics_text = f"""
            #### Evaluation Metrics:
            - Accuracy: {metrics['accuracy']:.4f}
            - Precision: {metrics['precision']:.4f}
            - Recall: {metrics['recall']:.4f}
            - F1 Score: {metrics['f1_score']:.4f}
            
            #### Confusion Matrix:
            - True Positives: {metrics['true_positives']}
            - False Positives: {metrics['false_positives']}
            - True Negatives: {metrics['true_negatives']}
            - False Negatives: {metrics['false_negatives']}
            """
            
            report_text = f"""
            ## Anomaly Detection Model Performance Report
            
            ### Model: {metrics['model_name']}
            
            #### Key Metrics:
            - Anomalies Detected: {metrics['anomaly_count']}
            - Total Records: {metrics['total_records']}
            - Anomaly Percentage: {metrics['anomaly_percent']:.2f}%
            - Threshold Used: {metrics['threshold_used']:.2f}
            {eval_metrics_text}
            
            #### Definitions:
            - Accuracy: Overall correctness of the model's predictions
            - Precision: Ratio of correctly identified anomalies to all predicted anomalies
            - Recall: Ratio of correctly identified anomalies to all actual anomalies
            - F1 Score: Harmonic mean of precision and recall
            
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
