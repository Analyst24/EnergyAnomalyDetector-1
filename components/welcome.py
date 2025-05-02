import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time

def show_welcome_page():
    # Set page title
    st.title("Energy & Efficiency Anomaly Detection")
    
    # Create layout with columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main content
        st.markdown("""
        ## Detect Anomalies with Machine Learning
        
        Identify abnormal patterns in your energy consumption data using advanced machine learning algorithms.
        """)
        
        # Create animated energy visualization
        chart_placeholder = st.empty()
        
        # Generate sample time series data for animation
        time_points = 100
        x = np.linspace(0, 10, time_points)
        
        # Create data for the animation
        for i in range(5):  # Show 5 frames of animation
            # Create a sine wave with random noise
            phase = i * 0.5
            y = 10 + 5 * np.sin(x + phase) + np.random.normal(0, 1, time_points)
            
            # Add anomalies at random positions
            anomaly_positions = np.random.choice(time_points, 3, replace=False)
            y[anomaly_positions] += np.random.uniform(5, 10, 3) * np.random.choice([-1, 1], 3)
            
            # Create DataFrame
            df = pd.DataFrame({
                'Time': x,
                'Energy': y,
                'Anomaly': [1 if i in anomaly_positions else 0 for i in range(time_points)]
            })
            
            # Create the plot
            fig = px.line(
                df, 
                x='Time', 
                y='Energy',
                title='Real-Time Energy Consumption Monitoring',
                template='plotly_dark'
            )
            
            # Add anomaly points
            anomalies = df[df['Anomaly'] == 1]
            fig.add_scatter(
                x=anomalies['Time'],
                y=anomalies['Energy'],
                mode='markers',
                marker=dict(color='red', size=10, symbol='circle'),
                name='Anomalies'
            )
            
            # Customize layout
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis_title="Time",
                yaxis_title="Energy Consumption",
                showlegend=True
            )
            
            # Display the plot
            chart_placeholder.plotly_chart(fig, use_container_width=True)
            
            # Add a slight delay to create animation effect
            time.sleep(0.7)
    
    with col2:
        # Feature highlights
        st.markdown("### Key Features")
        
        st.markdown("""
        - **Multiple ML Models**
          - Isolation Forest
          - Autoencoder Neural Network
          - K-Means Clustering
          
        - **Interactive Visualizations**
          - Time Series Analysis
          - Anomaly Distribution
          - Pattern Recognition
          
        - **Smart Recommendations**
          - Energy Saving Tips
          - Efficiency Improvements
          - Predictive Insights
        """)
    
    # Show energy efficiency gauge chart
    st.markdown("### Energy Efficiency Impact")
    
    # Create gauge chart
    fig = make_subplots(
        rows=1, 
        cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}]]
    )
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=87,
            title={"text": "Anomaly Detection Accuracy"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "green"},
                "steps": [
                    {"range": [0, 50], "color": "red"},
                    {"range": [50, 75], "color": "yellow"},
                    {"range": [75, 100], "color": "green"}
                ]
            }
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=23,
            title={"text": "Avg. Energy Savings Potential"},
            gauge={
                "axis": {"range": [0, 50], "suffix": "%"},
                "bar": {"color": "green"},
                "steps": [
                    {"range": [0, 10], "color": "lightgray"},
                    {"range": [10, 20], "color": "lightgreen"},
                    {"range": [20, 50], "color": "green"}
                ]
            },
            number={"suffix": "%"}
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        height=300, 
        template="plotly_dark",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Application workflow overview
    st.markdown("### How It Works")
    
    # Create workflow steps
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            """
            <div style='text-align: center;'>
                <h1 style='font-size: 2rem;'>📊</h1>
                <h4>Upload Data</h4>
                <p>Upload your energy consumption data in CSV format</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div style='text-align: center;'>
                <h1 style='font-size: 2rem;'>⚙️</h1>
                <h4>Configure Model</h4>
                <p>Select detection algorithm and sensitivity</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div style='text-align: center;'>
                <h1 style='font-size: 2rem;'>🔍</h1>
                <h4>Analyze Results</h4>
                <p>Visualize anomalies and patterns in your data</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        st.markdown(
            """
            <div style='text-align: center;'>
                <h1 style='font-size: 2rem;'>💡</h1>
                <h4>Get Recommendations</h4>
                <p>Receive actionable insights to improve efficiency</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown('<footer>© 2025 Opulent Chikwiramakomo. All rights reserved.</footer>', unsafe_allow_html=True)
