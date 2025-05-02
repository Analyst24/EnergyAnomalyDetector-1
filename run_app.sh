#!/bin/bash

# This script runs only the Streamlit frontend in standalone mode
# All functionality will work offline, but without database persistence
# It skips database initialization for faster loading

# Run the Streamlit app
echo "🚀 Starting Energy Anomaly Detection application in standalone mode (100% offline)..."
echo "✅ No database or additional services required"
streamlit run app.py --server.port 5000 --server.address 0.0.0.0