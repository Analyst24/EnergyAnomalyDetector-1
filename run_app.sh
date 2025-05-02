#!/bin/bash

# Initialize the database
echo "🔧 Initializing database..."
python initialize_db.py

# Run the Streamlit app
echo "🚀 Starting Energy Anomaly Detection application..."
streamlit run app.py --server.port 5000