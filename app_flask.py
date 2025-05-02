"""
Flask application that serves the Energy Anomaly Detection API
and integrates with the Streamlit frontend.
"""
import os
import json
import pandas as pd
from flask import Flask, jsonify, request, render_template, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import threading
import time

# Import backend modules if available
try:
    from backend.models import IsolationForestModel, AutoEncoderModel, KMeansModel
    from backend.preprocessing import preprocess_data
    from backend.utils import detect_contradictions, generate_recommendations
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    print("Backend modules not available, some functionality may be limited")

# Import database operations if available
try:
    from database.models import User
    from database.operations import (authenticate_user, create_user, get_user_by_username, 
                                    get_user_by_email, bulk_insert_energy_data,
                                    get_energy_data_for_user, save_anomaly_results)
    from database.connection import db_session, init_db
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Database modules not available, using file-based storage")

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "energy_anomaly_detection_secret_key")

# File path for user data (fallback method)
USERS_FILE = 'data/users.json'
ENERGY_DATA_DIR = 'data/energy/'

# Ensure necessary directories exist
def ensure_data_directories():
    """Ensure that data directories exist."""
    os.makedirs('data', exist_ok=True)
    os.makedirs(ENERGY_DATA_DIR, exist_ok=True)
    
    # Create users file if it doesn't exist
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)

# Get users from file (fallback method)
def get_users():
    """Get users from file if database is not available."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# Save users to file (fallback method)
def save_users(users):
    """Save users to file if database is not available."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Initialize Streamlit in a separate thread
def run_streamlit():
    """Run the Streamlit application in a separate process."""
    print("Starting Streamlit application...")
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return streamlit_process

# API routes 
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint for user login."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing username or password"}), 400
    
    # Try database authentication first if available
    if DATABASE_AVAILABLE:
        try:
            user = authenticate_user(username, password)
            if user:
                return jsonify({
                    "status": "success", 
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                })
        except Exception as e:
            print(f"Error during database authentication: {str(e)}")
    
    # Fallback to file-based authentication
    users = get_users()
    
    for user in users:
        if user['username'] == username and check_password_hash(user['password'], password):
            return jsonify({
                "status": "success", 
                "message": "Login successful",
                "user": {
                    "username": user['username'],
                    "email": user.get('email', '')
                }
            })
    
    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

@app.route('/api/signup', methods=['POST'])
def signup():
    """API endpoint for user registration."""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Check if username or email already exists
    if DATABASE_AVAILABLE:
        try:
            if get_user_by_username(username):
                return jsonify({"status": "error", "message": "Username already exists"}), 400
            
            if get_user_by_email(email):
                return jsonify({"status": "error", "message": "Email already exists"}), 400
            
            # Create user in database
            user = create_user(username, email, password)
            return jsonify({
                "status": "success", 
                "message": "User created successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }), 201
        except Exception as e:
            print(f"Error during database registration: {str(e)}")
    
    # Fallback to file-based registration
    users = get_users()
    
    # Check if username or email already exists
    for user in users:
        if user['username'] == username:
            return jsonify({"status": "error", "message": "Username already exists"}), 400
        if user.get('email') == email:
            return jsonify({"status": "error", "message": "Email already exists"}), 400
    
    # Add new user
    users.append({
        'username': username,
        'email': email,
        'password': generate_password_hash(password)
    })
    
    # Save updated users list
    save_users(users)
    
    return jsonify({
        "status": "success", 
        "message": "User created successfully",
        "user": {
            "username": username,
            "email": email
        }
    }), 201

@app.route('/api/detect_anomalies', methods=['POST'])
def detect_anomalies():
    """API endpoint for anomaly detection."""
    data = request.json
    username = data.get('username')
    dataset = data.get('data')
    model_name = data.get('model', 'isolation_forest')
    threshold = float(data.get('threshold', 0.5))
    
    if not username or not dataset:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Convert dataset to DataFrame if it's not already
    if isinstance(dataset, list):
        try:
            df = pd.DataFrame(dataset)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error converting data: {str(e)}"}), 400
    elif isinstance(dataset, dict):
        try:
            df = pd.DataFrame.from_dict(dataset)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error converting data: {str(e)}"}), 400
    else:
        return jsonify({"status": "error", "message": "Invalid data format"}), 400
    
    # Preprocess data if backend is available
    if BACKEND_AVAILABLE:
        try:
            df = preprocess_data(df)
            
            # Select model based on model_name
            if model_name == 'isolation_forest':
                model = IsolationForestModel()
            elif model_name == 'autoencoder':
                model = AutoEncoderModel()
            elif model_name == 'kmeans':
                model = KMeansModel()
            else:
                # Default to isolation forest
                model = IsolationForestModel()
            
            # Detect anomalies
            results_df, metrics = model.detect(df, threshold=threshold)
            
            # Detect contradictions
            contradictions = detect_contradictions(results_df)
            
            # Generate recommendations
            recommendations = generate_recommendations(results_df)
            
            # Save results to database if available
            if DATABASE_AVAILABLE:
                try:
                    # Get user object
                    user = get_user_by_username(username)
                    if user:
                        # Save energy data
                        energy_data = bulk_insert_energy_data(user.id, df)
                        
                        # Save anomaly results
                        anomaly_results = save_anomaly_results(user.id, results_df, model_name)
                except Exception as e:
                    print(f"Error saving to database: {str(e)}")
            
            # Return results
            return jsonify({
                "status": "success",
                "message": "Anomaly detection completed successfully",
                "results": results_df.to_dict(orient='records'),
                "metrics": metrics,
                "contradictions": contradictions,
                "recommendations": recommendations
            })
        except Exception as e:
            return jsonify({"status": "error", "message": f"Error during anomaly detection: {str(e)}"}), 500
    else:
        return jsonify({"status": "error", "message": "Backend modules not available"}), 501

# Main route redirects to Streamlit
@app.route('/')
def index():
    """Main route redirects to Streamlit frontend."""
    return redirect('http://localhost:5000')

if __name__ == '__main__':
    # Ensure data directories exist
    ensure_data_directories()
    
    # Initialize database if available
    if DATABASE_AVAILABLE:
        try:
            init_db()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
    
    # Start Streamlit in a separate thread
    streamlit_thread = threading.Thread(target=run_streamlit)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Give Streamlit a moment to start
    time.sleep(2)
    
    # Start Flask app - use a different port than Streamlit
    app.run(host='0.0.0.0', port=8000, debug=False)