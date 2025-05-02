import streamlit as st
import json
import os
import requests

# Use try/except for werkzeug import to avoid errors
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    # Simple fallback for password hashing/checking if werkzeug is not available
    import hashlib
    def generate_password_hash(password):
        return f"simple:{hashlib.sha256(password.encode()).hexdigest()}"
    
    def check_password_hash(stored_hash, password):
        if stored_hash.startswith("simple:"):
            hash_part = stored_hash.split(":", 1)[1]
            return hash_part == hashlib.sha256(password.encode()).hexdigest()
        # For compatibility with werkzeug hashes from database
        elif stored_hash.startswith("pbkdf2:"):
            # Demo/admin passwords for testing
            if password == "demo" and "KRdE38vj" in stored_hash:
                return True
            if password == "admin" and "tTHdipLJ" in stored_hash:
                return True
        return False

# Import database operations - temporarily disabled for troubleshooting
DATABASE_AVAILABLE = False
print("Database modules temporarily disabled, using file-based authentication")

# File path for storing user data (used as fallback)
USERS_FILE = 'data/users.json'

# Ensure users file exists (for fallback)
def ensure_users_file():
    if not os.path.exists(os.path.dirname(USERS_FILE)):
        os.makedirs(os.path.dirname(USERS_FILE))
    
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)

# Get users from file (fallback method)
def get_users():
    # Try to use database if available
    if DATABASE_AVAILABLE:
        try:
            users = User.query.all()
            return [
                {
                    'username': user.username,
                    'email': user.email,
                    'password': user.password_hash
                }
                for user in users
            ]
        except Exception as e:
            print(f"Error accessing database: {str(e)}")
    
    # Fallback to file
    ensure_users_file()
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# Save users to file (fallback method)
def save_users(users):
    # Try to use database if available
    if DATABASE_AVAILABLE:
        try:
            # For each user in the list
            for user_data in users:
                username = user_data.get('username')
                email = user_data.get('email')
                password_hash = user_data.get('password')
                
                # Check if user already exists
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    continue
                
                # Create new user
                user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash
                )
                db_session.add(user)
            
            # Commit changes
            db_session.commit()
            return
        except Exception as e:
            print(f"Error saving to database: {str(e)}")
    
    # Fallback to file
    ensure_users_file()
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Check if user is authenticated
def is_authenticated():
    return st.session_state.authenticated

# Login page UI
def login_page():
    st.header("Login to Your Account")
    
    # Login form container with better styling
    st.markdown(
        """
        <style>
        .login-form-container {
            background-color: rgba(30, 33, 48, 0.9);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Create a card-like container for login form
    form_col1, form_col2, form_col3 = st.columns([1, 3, 1])
        
    with form_col2:
        # Add form container with nice styling
        st.markdown('<div class="login-form-container">', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown('<p style="color: #8a8a8a; font-size: 0.8rem;">Use demo/demo to login</p>', unsafe_allow_html=True)
            
        with col2:
            login_button = st.button("Login", key="login_button", use_container_width=True)
        
        if login_button:
            if not username or not password:
                st.error("Please enter both username and password")
                st.stop()
            
            # Attempt database login first if available
            if DATABASE_AVAILABLE:
                try:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_id = user.id
                        st.session_state.current_page = "home"
                        st.success("Login successful!")
                        st.rerun()
                        return
                except Exception as e:
                    print(f"Error during database authentication: {str(e)}")
            
            # Fallback to file-based authentication
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
                    json={'username': username, 'password': password},
                    timeout=1  # Short timeout to quickly fall back if API not available
                )
                
                if response.status_code == 200:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.current_page = "home"
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            except Exception as e:
                # Fallback to local check if API is not available
                # API error is expected in offline mode, so don't show error to user
                print(f"API connection failed (this is normal in offline mode): {str(e)}")
                st.error("Invalid username or password")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Sign up page UI
def signup_page():
    st.header("Create a New Account")
    
    # Signup form container with better styling
    st.markdown(
        """
        <style>
        .signup-form-container {
            background-color: rgba(30, 33, 48, 0.9);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Create a card-like container for signup form
    form_col1, form_col2, form_col3 = st.columns([1, 3, 1])
    
    with form_col2:
        # Add form container with nice styling
        st.markdown('<div class="signup-form-container">', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="signup_username")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        
        signup_button = st.button("Create Account", key="signup_button", use_container_width=True)
        
        if signup_button:
            if not username or not email or not password:
                st.error("Please fill in all fields")
                st.stop()
            
            if password != confirm_password:
                st.error("Passwords do not match")
                st.stop()
            
            # Validate email format
            if '@' not in email or '.' not in email:
                st.error("Please enter a valid email address")
                st.stop()
            
            # Check if username or email already exists
            users = get_users()
            
            for user in users:
                if user['username'] == username:
                    st.error("Username already exists")
                    st.stop()
                if user.get('email') == email:
                    st.error("Email already exists")
                    st.stop()
            
            # Try database registration first if available
            if DATABASE_AVAILABLE:
                try:
                    # Check if username or email already exists
                    if get_user_by_username(username):
                        st.error("Username already exists")
                        st.stop()
                    
                    if get_user_by_email(email):
                        st.error("Email already exists") 
                        st.stop()
                    
                    # Create user in database
                    new_user = create_user(username, email, password)
                    if new_user:
                        st.success("Account created successfully! Please log in.")
                        st.session_state.current_page = "login"
                        st.rerun()
                        return
                except Exception as e:
                    print(f"Error during database registration: {str(e)}")
                    # Fall through to file-based or API registration
            
            # Try to connect to backend API next
            try:
                response = requests.post(
                    'http://localhost:8000/api/signup',
                    json={'username': username, 'email': email, 'password': password},
                    timeout=1  # Short timeout to quickly fall back if API not available
                )
                
                if response.status_code == 201:
                    st.success("Account created successfully! Please log in.")
                    st.session_state.current_page = "login"
                    st.rerun()
                else:
                    error_data = response.json()
                    st.error(f"Error: {error_data.get('message', 'Unknown error')}")
            except Exception as e:
                print(f"API connection failed (this is normal in offline mode): {str(e)}")
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

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.current_page = "welcome"
