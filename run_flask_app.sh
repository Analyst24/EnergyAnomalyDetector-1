#!/bin/bash

# This script starts both the Flask backend API and the Streamlit frontend
# Use this when you want the complete integrated system

# Run Flask API in the background
echo "🔧 Starting Flask API backend..."
python app_flask.py &
FLASK_PID=$!

# Give Flask a moment to start
sleep 2

# Keeping the process running
echo "✅ System is running. Press Ctrl+C to stop."
wait $FLASK_PID

# Function to clean up on exit
function cleanup {
    echo "🛑 Stopping services..."
    kill $FLASK_PID
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Keep script running
while true; do
    sleep 1
done