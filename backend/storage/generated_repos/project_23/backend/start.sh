#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

VENV_DIR=".venv"

echo "Checking for virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting FastAPI application..."
# Run with reload for development
uvicorn main:app --reload --host 0.0.0.0 --port 8000
