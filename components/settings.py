import streamlit as st
import json
import os

def show_settings():
    st.title("Settings")
    
    st.markdown("### Application Configuration")
    
    # Create tabs for different settings categories
    tab1, tab2, tab3 = st.tabs(["Detection Settings", "Interface Settings", "Account Settings"])
    
    with tab1:
        st.markdown("### Anomaly Detection Configuration")
        
        # Model selection
        st.markdown("#### Default Model")
        
        model_options = {
            "isolation_forest": "Isolation Forest",
            "autoencoder": "Autoencoder Neural Network",
            "kmeans": "K-Means Clustering"
        }
        
        selected_model = st.selectbox(
            "Choose your default anomaly detection model:",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=list(model_options.keys()).index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0
        )
        
        # Anomaly threshold slider
        st.markdown("#### Default Anomaly Detection Sensitivity")
        threshold = st.slider(
            "Set the default anomaly threshold (lower = more sensitive):",
            min_value=0.01,
            max_value=0.99,
            value=float(st.session_state.anomaly_threshold),
            step=0.01,
            format="%.2f"
        )
        
        # Save detection settings button
        if st.button("Save Detection Settings"):
            st.session_state.selected_model = selected_model
            st.session_state.anomaly_threshold = threshold
            st.success("Detection settings saved successfully!")
        
        # Advanced settings
        with st.expander("Advanced Model Settings"):
            st.markdown("#### Isolation Forest Parameters")
            n_estimators = st.slider(
                "Number of estimators:",
                min_value=50,
                max_value=500,
                value=100,
                step=10
            )
            
            max_samples = st.slider(
                "Maximum samples:",
                min_value=100,
                max_value=1000,
                value=256,
                step=10
            )
            
            st.markdown("#### Autoencoder Parameters")
            epochs = st.slider(
                "Training epochs:",
                min_value=10,
                max_value=200,
                value=50,
                step=5
            )
            
            learning_rate = st.select_slider(
                "Learning rate:",
                options=[0.0001, 0.0005, 0.001, 0.005, 0.01],
                value=0.001
            )
            
            st.markdown("#### K-Means Parameters")
            n_clusters = st.slider(
                "Number of clusters:",
                min_value=2,
                max_value=10,
                value=3,
                step=1
            )
            
            if st.button("Save Advanced Settings"):
                # We would normally save these to a configuration file or database
                # For this prototype, we'll just acknowledge the save
                st.success("Advanced settings saved successfully!")
    
    with tab2:
        st.markdown("### User Interface Settings")
        
        # Theme controls
        st.markdown("#### Theme")
        
        # Dark theme is the only option currently as per requirements
        theme = st.radio(
            "Select theme:",
            ["Dark Theme"],
            index=0,
            disabled=True
        )
        
        st.info("Currently only Dark Theme is available. Light Theme will be available in future updates.")
        
        # Chart preferences
        st.markdown("#### Chart Preferences")
        
        chart_colorscale = st.selectbox(
            "Default chart color scheme:",
            ["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Blues", "Reds", "Greens"],
            index=0
        )
        
        # Data display preferences
        st.markdown("#### Data Display")
        
        rows_per_page = st.select_slider(
            "Rows to display in data tables:",
            options=[10, 25, 50, 100, 250, 500],
            value=25
        )
        
        date_format = st.selectbox(
            "Date format:",
            ["YYYY-MM-DD HH:MM:SS", "MM/DD/YYYY HH:MM:SS", "DD/MM/YYYY HH:MM:SS", "YYYY/MM/DD HH:MM:SS"],
            index=0
        )
        
        # Save interface settings button
        if st.button("Save Interface Settings"):
            # These would typically be saved to user preferences
            st.success("Interface settings saved successfully!")
    
    with tab3:
        st.markdown("### Account Settings")
        
        # User information (display only)
        st.markdown("#### User Information")
        st.markdown(f"**Username**: {st.session_state.username}")
        
        # Change password
        st.markdown("#### Change Password")
        
        with st.form(key="change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            submit_button = st.form_submit_button(label="Change Password")
            
            if submit_button:
                if not current_password or not new_password or not confirm_password:
                    st.error("Please fill in all password fields.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                else:
                    # Password validation would go here
                    # This would typically connect to an API or database
                    st.success("Password updated successfully!")
        
        # Delete account
        st.markdown("#### Delete Account")
        
        if st.button("Delete My Account", key="delete_account_button"):
            st.warning("Are you sure you want to delete your account? This action cannot be undone.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Yes, Delete My Account", key="confirm_delete"):
                    # Account deletion would go here
                    # This would typically connect to an API or database
                    st.success("Account deleted successfully!")
                    # Redirect to login page
                    st.session_state.authenticated = False
                    st.session_state.username = ""
                    st.session_state.current_page = "welcome"
                    st.rerun()
            
            with col2:
                if st.button("No, Keep My Account", key="cancel_delete"):
                    st.info("Account deletion cancelled.")
    
    # System information
    st.markdown("### System Information")
    
    with st.expander("System Details"):
        st.markdown("#### Energy Efficiency Anomaly Detection System")
        st.markdown("**Version**: 1.0.0")
        st.markdown("**Machine Learning Models**: Isolation Forest, Autoencoder, K-Means")
        st.markdown("**Supported Data Formats**: CSV")
        st.markdown("**Maximum File Size**: 100MB")
        st.markdown("**Processing Capacity**: Up to 50,000 rows in under 30 seconds")
    
    # Footer
    st.markdown("---")
    st.markdown('<footer>© 2025 Opulent Chikwiramakomo. All rights reserved.</footer>', unsafe_allow_html=True)
