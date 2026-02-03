#!/bin/bash

# Check if venv exists, if not, create it and install dependencies
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
  echo "Installing dependencies..."
  source venv/bin/activate
  pip install -r requirements.txt
else
  echo "Activating virtual environment..."
  source venv/bin/activate
  # Optional: Ensure dependencies are up-to-date
  # pip install -r requirements.txt
fi

echo "Starting FastAPI application..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
