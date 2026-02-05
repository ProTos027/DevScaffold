#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

VENV_DIR="venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
