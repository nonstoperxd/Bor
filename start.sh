#!/bin/bash

# Start script for Render deployment
echo "Starting Telegram OTP Bot on Render..."

# Set environment variables
export DISPLAY=:99
export PYTHONUNBUFFERED=1

# Start virtual display (for headless browser)
Xvfb :99 -screen 0 1920x1080x24 &

# Wait for display to be ready
sleep 2

# Start the application with health server
python health_server.py