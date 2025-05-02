import streamlit as st
import json
import os
import requests
from werkzeug.security import generate_password_hash, check_password_hash

# File path for storing user data
USERS_FILE = 'data/users.json'

# Ensure users file exists
def ensure_users_file():
    if not os.path.exists(os.path.dirname(USERS_FILE)):
        os.makedirs(os.path.dirname(USERS_FILE))
    
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)

# Get users from file
def get_users():
    ensure_users_file()
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# Save users to file
def save_users(users):
    ensure_users_file()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Check if user is authenticated
def is_authenticated():
    return st.session_state.authenticated

# Login page UI
def login_page():
    st.title("Login")
    
    # Set a background image
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://img.freepik.com/free-vector/gradient-network-connection-background_23-2148865392.jpg");
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Create a card-like container for login form
    with st.container():
        st.markdown(
            """
            <style>
            .login-container {
                background-color: rgba(25, 25, 25, 0.8);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_button"):
            if not username or not password:
                st.error("Please enter both username and password")
                return
            
            # Attempt login locally first
            users = get_users()
            
            for user in users:
                if user['username'] == username and check_password_hash(user['password'], password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.current_page = "home"
                    st.success("Login successful!")
                    st.rerun()
                    return
            
            # If not successful, try to connect to backend API
            try:
                response = requests.post(
                    'http://localhost:8000/api/login',
                    json={'username': username, 'password': password}
                )
                
                if response.status_code == 200:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.current_page = "home"
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            except:
                # Fallback to local check if API is not available
                st.error("Could not connect to authentication service. Invalid username or password.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("Don't have an account? Sign up!")

# Sign up page UI
def signup_page():
    st.title("Sign Up")
    
    # Set a background image
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://img.freepik.com/free-vector/gradient-network-connection-background_23-2148865392.jpg");
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Create a card-like container for signup form
    with st.container():
        st.markdown(
            """
            <style>
            .signup-container {
                background-color: rgba(25, 25, 25, 0.8);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('<div class="signup-container">', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        
        if st.button("Sign Up", key="signup_button"):
            if not username or not email or not password:
                st.error("Please fill in all fields")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            # Validate email format
            if '@' not in email or '.' not in email:
                st.error("Please enter a valid email address")
                return
            
            # Check if username or email already exists
            users = get_users()
            
            for user in users:
                if user['username'] == username:
                    st.error("Username already exists")
                    return
                if user.get('email') == email:
                    st.error("Email already exists")
                    return
            
            # Try to connect to backend API first
            try:
                response = requests.post(
                    'http://localhost:8000/api/signup',
                    json={'username': username, 'email': email, 'password': password}
                )
                
                if response.status_code == 201:
                    st.success("Account created successfully! Please log in.")
                    st.session_state.current_page = "login"
                    st.rerun()
                else:
                    error_data = response.json()
                    st.error(f"Error: {error_data.get('message', 'Unknown error')}")
            except:
                # Fallback to local registration if API is not available
                # Add new user to users list
                users.append({
                    'username': username,
                    'email': email,
                    'password': generate_password_hash(password)
                })
                
                # Save updated users list
                save_users(users)
                
                st.success("Account created successfully! Please log in.")
                st.session_state.current_page = "login"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("Already have an account? Log in!")

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.current_page = "welcome"
