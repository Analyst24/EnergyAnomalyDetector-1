#!/bin/bash

# Run the Streamlit app directly, skipping database initialization 
# for troubleshooting
echo "🚀 Starting Energy Anomaly Detection application..."
streamlit run app.py --server.port 5000 --server.address 0.0.0.0