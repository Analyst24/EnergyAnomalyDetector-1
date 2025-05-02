#!/bin/bash

# This script runs only the Streamlit frontend in standalone mode
# All functionality will work offline, but without database persistence
# It skips database initialization for faster loading

# Create required data directories
mkdir -p data
mkdir -p data/energy

# Ensure .streamlit directory exists
mkdir -p .streamlit

# Check if config.toml exists, create if missing
if [ ! -f .streamlit/config.toml ]; then
  cat > .streamlit/config.toml << EOF
[server]
headless = true
enableCORS = false
address = "0.0.0.0"
port = 5000
enableXsrfProtection = false

[browser]
serverAddress = "localhost"

[theme]
primaryColor = "#4CAF50"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#1a1a1a"
textColor = "#FFFFFF"
EOF
fi

# Run the Streamlit app
echo "🚀 Starting Energy Anomaly Detection application in standalone mode (100% offline)..."
echo "✅ No database or additional services required"
echo "🌐 Access the application at http://localhost:5000"

# Run using Streamlit configuration file
streamlit run app.py