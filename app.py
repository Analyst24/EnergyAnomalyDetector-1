import streamlit as st
import os
import json
import requests
import pandas as pd
from PIL import Image

# Initialize database if available - temporarily disabled for troubleshooting
print("Database connection temporarily disabled for troubleshooting")

# Set database flag for session state
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False

# Import components
from components.authentication import login_page, signup_page, is_authenticated, logout
from components.welcome import show_welcome_page
from components.home import show_home_page
from components.dashboard import show_dashboard
from components.data_upload import show_data_upload
from components.detection import show_detection_page
from components.results import show_results_page
from components.model_insights import show_model_insights
from components.recommendations import show_recommendations
from components.settings import show_settings

# Set page configuration
st.set_page_config(
    page_title="Energy Efficiency Anomaly Detection",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply dark theme with custom CSS
st.markdown("""
<style>
    .reportview-container {
        background-color: #0e1117;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #1a1a1a;
        color: white;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #2b2b2b;
        color: white;
    }
    footer {
        font-size: 0.8rem;
        color: #888888;
        text-align: center;
        padding: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "welcome"
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'detection_results' not in st.session_state:
    st.session_state.detection_results = None
if 'model_metrics' not in st.session_state:
    st.session_state.model_metrics = None
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "isolation_forest"  # Default model
if 'anomaly_threshold' not in st.session_state:
    st.session_state.anomaly_threshold = 0.5  # Default threshold

# Main content
def main():
    # Show welcome page if not authenticated
    if not st.session_state.authenticated and st.session_state.current_page == "welcome":
        show_welcome_page()
        if st.button("Get Started"):
            st.session_state.current_page = "login"
            st.rerun()
    
    # Show login/signup if not authenticated
    elif not st.session_state.authenticated:
        # Display authentication options with tabs
        auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up"])
        
        with auth_tab1:
            login_page()
            
        with auth_tab2:
            signup_page()
    
    # Show main interface if authenticated
    else:
        # Sidebar navigation
        with st.sidebar:
            st.title(f"Welcome, {st.session_state.username}")
            
            if st.button("Home"):
                st.session_state.current_page = "home"
                st.rerun()
            
            if st.button("Dashboard"):
                st.session_state.current_page = "dashboard"
                st.rerun()
                
            if st.button("Upload Data"):
                st.session_state.current_page = "upload"
                st.rerun()
                
            if st.button("Run Detection"):
                st.session_state.current_page = "detection"
                st.rerun()
                
            if st.button("Results"):
                st.session_state.current_page = "results"
                st.rerun()
                
            if st.button("Model Insights"):
                st.session_state.current_page = "insights"
                st.rerun()
                
            if st.button("Recommendations"):
                st.session_state.current_page = "recommendations"
                st.rerun()
                
            if st.button("Settings"):
                st.session_state.current_page = "settings"
                st.rerun()
                
            if st.button("Logout"):
                logout()
                st.rerun()
        
        # Display the selected page
        if st.session_state.current_page == "home":
            show_home_page()
        elif st.session_state.current_page == "dashboard":
            show_dashboard()
        elif st.session_state.current_page == "upload":
            show_data_upload()
        elif st.session_state.current_page == "detection":
            show_detection_page()
        elif st.session_state.current_page == "results":
            show_results_page()
        elif st.session_state.current_page == "insights":
            show_model_insights()
        elif st.session_state.current_page == "recommendations":
            show_recommendations()
        elif st.session_state.current_page == "settings":
            show_settings()
    
    # Footer - present on all pages
    st.markdown("---")
    st.markdown('<footer>© 2025 Opulent Chikwiramakomo. All rights reserved.</footer>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
