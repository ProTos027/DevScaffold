#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

VENV_PATH=".venv"
REQUIREMENTS_FILE="requirements.txt"

echo "Starting FastAPI project..."

# Check if virtual environment exists, create if not
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"
echo "Virtual environment activated."

# Install dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --no-cache-dir -r "$REQUIREMENTS_FILE"
    echo "Dependencies installed."
else
    echo "Warning: $REQUIREMENTS_FILE not found. Skipping dependency installation."
fi

# Run FastAPI application
echo "Starting Uvicorn server..."
# --reload for development, remove for production
uvicorn main:app --reload --host 0.0.0.0 --port 8000
