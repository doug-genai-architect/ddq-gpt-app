#!/usr/bin/env bash
set -e

# Install Python dependencies if not already installed
pip install --upgrade pip
pip install -r requirements.txt

# Start the Flask app using gunicorn
exec gunicorn -k gthread -w 4 -b 0.0.0.0:${PORT:-8000} app:app 