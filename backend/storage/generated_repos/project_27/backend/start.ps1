# PowerShell script to set up and run the FastAPI application

# Exit immediately if a command fails
$ErrorActionPreference = "Stop"

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Please install it to continue."
    exit 1
}

# Create a virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
. .venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the FastAPI application
Write-Host "Starting FastAPI application..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
