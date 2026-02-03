# Check if venv exists, if not, create it and install dependencies
if (-Not (Test-Path ".\venv")) {
  Write-Host "Creating virtual environment..."
  python -m venv venv
  Write-Host "Installing dependencies..."
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
} else {
  Write-Host "Activating virtual environment..."
  .\venv\Scripts\Activate.ps1
  # Optional: Ensure dependencies are up-to-date
  # pip install -r requirements.txt
}

Write-Host "Starting FastAPI application..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
