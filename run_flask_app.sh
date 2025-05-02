#!/bin/bash

# This script starts both the Flask backend API and the Streamlit frontend
# Use this when you want the complete integrated system with enhanced features

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

# Run Flask API in the background
echo "🔧 Starting Flask API backend on port 8000..."
python app_flask.py &
FLASK_PID=$!

# Give Flask a moment to start
sleep 2

echo "🚀 System is running in integrated mode (with both Flask backend and Streamlit frontend)"
echo "🌐 Access the application at http://localhost:5000"
echo "📌 Note: The system is still 100% offline-compatible"
echo "✅ Press Ctrl+C to stop all services"

# Function to clean up on exit
function cleanup {
    echo "🛑 Stopping services..."
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null
    fi
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Keep script running
while true; do
    # Check if Flask process is still running
    if ! ps -p $FLASK_PID > /dev/null; then
        echo "⚠️ Flask process exited, restarting..."
        python app_flask.py &
        FLASK_PID=$!
    fi
    sleep 5
done