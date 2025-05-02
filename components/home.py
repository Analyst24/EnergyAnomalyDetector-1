import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time

def show_home_page():
    st.title("Home")
    
    # Welcome message
    st.markdown(f"""
    ## Welcome to the Energy Efficiency Anomaly Detection System
    
    This advanced system helps you identify anomalies in your energy consumption data using state-of-the-art machine learning algorithms.
    
    ### Available Models:
    - **Isolation Forest**: Effective at isolating outliers in the data
    - **Autoencoder Neural Network**: Deep learning approach for complex pattern recognition
    - **K-Means Clustering**: Unsupervised clustering to identify unusual patterns
    
    Navigate through the sidebar to explore the system's features.
    """)
    
    # Create tabs for different visual sections
    tab1, tab2 = st.tabs(["System Overview", "Energy Insights"])
    
    with tab1:
        # Create animated visual - Energy Consumption Pattern
        st.markdown("### Energy Consumption Patterns")
        
        # Create animated time series data
        chart_placeholder = st.empty()
        
        # Generate sample time series data for animation
        def generate_time_series(step):
            # Create a time series with baseline seasonal pattern
            hours = np.arange(0, 24)
            base_pattern = 100 + 50 * np.sin(np.pi * hours / 12) + 20 * np.cos(np.pi * hours / 6)
            
            # Add randomness
            random_factor = np.random.normal(0, 10, size=24)
            
            # Add an anomaly that moves with each step
            anomaly_position = (step % 24)
            anomaly = np.zeros(24)
            anomaly[anomaly_position] = 100  # Large spike
            
            # Combine
            pattern = base_pattern + random_factor + anomaly
            
            return pd.DataFrame({
                'hour': hours,
                'consumption': pattern,
                'is_anomaly': [1 if i == anomaly_position else 0 for i in range(24)]
            })
        
        # Function to update chart
        def update_chart(step):
            data = generate_time_series(step)
            
            fig = px.line(
                data,
                x='hour',
                y='consumption',
                title='Real-time Energy Consumption Monitoring',
                template='plotly_dark'
            )
            
            # Add anomaly points
            anomalies = data[data['is_anomaly'] == 1]
            fig.add_scatter(
                x=anomalies['hour'],
                y=anomalies['consumption'],
                mode='markers',
                marker=dict(color='red', size=12, symbol='circle'),
                name='Anomaly Detected'
            )
            
            fig.update_layout(
                xaxis_title='Hour of Day',
                yaxis_title='Energy Consumption (kWh)',
                height=400,
                showlegend=True
            )
            
            return fig
        
        # Simulate real-time updates for a few steps then stop
        for i in range(10):
            chart_placeholder.plotly_chart(update_chart(i), use_container_width=True)
            time.sleep(0.5)
        
        # System capabilities section with icons
        st.markdown("### System Capabilities")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="text-align:center">
                <h3>📊</h3>
                <h4>Data Visualization</h4>
                <p>Interactive charts and dashboards</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align:center">
                <h3>🤖</h3>
                <h4>ML Detection</h4>
                <p>Advanced anomaly detection algorithms</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="text-align:center">
                <h3>📝</h3>
                <h4>Recommendations</h4>
                <p>Actionable insights for energy efficiency</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        # Energy efficiency animation/visualization
        st.markdown("### Energy Efficiency Metrics")
        
        # Create a gauge chart for efficiency score
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=78,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Energy Efficiency Score"},
            delta={'reference': 70, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 50], 'color': "red"},
                    {'range': [50, 75], 'color': "yellow"},
                    {'range': [75, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            template='plotly_dark'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add more visuals - Energy consumption by category
        st.markdown("### Energy Consumption by Category")
        
        # Sample data for a pie chart
        categories = ['HVAC', 'Lighting', 'Equipment', 'IT Systems', 'Other']
        values = [42, 19, 22, 11, 6]
        
        fig = px.pie(
            values=values,
            names=categories,
            title='Energy Usage Distribution',
            template='plotly_dark',
            hole=0.4
        )
        
        # Update layout for dark theme
        fig.update_layout(
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Animated consumption trend
        st.markdown("### Annual Energy Consumption Trend")
        
        # Generate monthly data with seasonal pattern
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        current_year = np.array([1050, 980, 920, 870, 790, 820, 950, 1020, 890, 950, 1080, 1150])
        previous_year = current_year * 1.2  # 20% higher consumption last year
        
        # Create a DataFrame
        df = pd.DataFrame({
            'Month': months * 2,
            'Year': ['Current Year'] * 12 + ['Previous Year'] * 12,
            'Consumption': np.concatenate([current_year, previous_year])
        })
        
        # Create bar chart
        fig = px.bar(
            df,
            x='Month',
            y='Consumption',
            color='Year',
            barmode='group',
            title='Year-over-Year Energy Consumption Comparison',
            template='plotly_dark',
            color_discrete_map={'Current Year': '#4CAF50', 'Previous Year': '#9E9E9E'}
        )
        
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Energy Consumption (kWh)',
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
