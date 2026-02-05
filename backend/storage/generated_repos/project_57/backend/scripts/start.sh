#!/bin/bash

# --- Virtual Environment Setup ---
VENV_DIR=".venv"
PYTHON_EXEC="python3"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR/..."
    "$PYTHON_EXEC" -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR"/bin/activate

# --- Install Dependencies ---
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install --no-cache-dir -r requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

# --- Run FastAPI Application ---
echo "Starting FastAPI application..."
# --host 0.0.0.0 for external access, --port 8000 is default
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

deactivate
echo "Application stopped. Virtual environment deactivated."