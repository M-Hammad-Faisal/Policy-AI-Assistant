#!/usr/bin/env bash

# Cloud Run assigns the PORT environment variable.
PORT=${PORT:-8080}

# Define the absolute path to the Python executable inside the venv
# Note: In Docker, the venv is at /app/.venv/bin/python
PYTHON_EXECUTABLE=/app/.venv/bin/python

# Start the main Slack Bot application, binding it to the exposed port.
# You need to adjust app.py to listen on the $PORT variable.
echo "Starting Socket Mode Slack Bot on port $PORT..."
exec "$PYTHON_EXECUTABLE" src/policy_assistant/app.py