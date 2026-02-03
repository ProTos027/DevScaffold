#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if Python 3 is available
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is not installed. Please install it to continue."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the FastAPI application
echo "Starting FastAPI application..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
