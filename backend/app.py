import os
import numpy as np
import pandas as pd
import json
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import IsolationForestModel, AutoEncoderModel, KMeansModel
from preprocessing import preprocess_data
from utils import detect_contradictions, generate_recommendations

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Initialize models
isolation_forest = IsolationForestModel()
autoencoder = AutoEncoderModel()
kmeans = KMeansModel()

USERS_FILE = '../data/users.json'

# Create users file if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump([], f)

def get_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    users = get_users()
    
    # Check if username or email already exists
    for user in users:
        if user['username'] == username:
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        if user['email'] == email:
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    # Add new user
    users.append({
        'username': username,
        'email': email,
        'password': generate_password_hash(password)
    })
    
    save_users(users)
    
    return jsonify({'success': True, 'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    users = get_users()
    
    for user in users:
        if user['username'] == username and check_password_hash(user['password'], password):
            return jsonify({'success': True, 'username': username}), 200
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/detect', methods=['POST'])
def detect_anomalies():
    # Get request data
    data = request.json
    df = pd.DataFrame(data['data'])
    model_name = data['model']
    threshold = float(data.get('threshold', 0.5))
    
    # Preprocess data
    preprocessed_data = preprocess_data(df)
    
    # Check for contradictions in data
    contradictions = detect_contradictions(preprocessed_data)
    
    # Run appropriate model for anomaly detection
    if model_name == 'isolation_forest':
        results, metrics = isolation_forest.detect(preprocessed_data, threshold)
    elif model_name == 'autoencoder':
        results, metrics = autoencoder.detect(preprocessed_data, threshold)
    elif model_name == 'kmeans':
        results, metrics = kmeans.detect(preprocessed_data, threshold)
    else:
        return jsonify({'error': 'Invalid model name'}), 400
    
    # Generate recommendations based on anomalies
    recommendations = generate_recommendations(results)
    
    # Prepare response
    response = {
        'results': results.to_dict(orient='records'),
        'metrics': metrics,
        'contradictions': contradictions,
        'recommendations': recommendations
    }
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
