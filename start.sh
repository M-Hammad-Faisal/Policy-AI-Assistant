#!/bin/bash

# Cloud Run assigns the PORT environment variable.
PORT=${PORT:-8080}

# Define the absolute path to the Python executable inside the venv
PYTHON_EXECUTABLE=$(pwd)"/.venv/bin/python"

# 1. Start the main Slack Bot application in the background.
echo "Starting Socket Mode Slack Bot..."
$PYTHON_EXECUTABLE src/policy_assistant/app.py &

# 2. Start a simple HTTP server to satisfy the Cloud Run health check.
echo "Starting Dummy HTTP server on port $PORT..."
/usr/local/bin/python -m http.server $PORT