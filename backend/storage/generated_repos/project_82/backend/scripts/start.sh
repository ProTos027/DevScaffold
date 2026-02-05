#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

VENV_DIR="venv"

# Check if virtual environment exists, if not, create it
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing/Upgrading dependencies..."
pip install -r requirements.txt

# Run the FastAPI application
echo "Starting FastAPI application..."
# The --reload flag is great for development
# For production, remove --reload and consider a process manager like Gunicorn or systemd
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload