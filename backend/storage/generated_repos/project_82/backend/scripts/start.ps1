# Exit immediately if a command exits with a non-zero status.
$ErrorActionPreference = "Stop"

$VENV_DIR = "venv"

# Check if virtual environment exists, if not, create it
If (-not (Test-Path -Path $VENV_DIR)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VENV_DIR
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
# On Windows, activate.ps1 might be blocked by execution policy.
# A safer way is to directly invoke the python interpreter from venv.
# .\venv\Scripts\Activate.ps1 # This is commented out because it might require changing execution policy.
# Instead, we will ensure python and pip commands point to the venv.

# Ensure pip and python commands point to the venv
$env:PATH = (Join-Path (Get-Item -Path $VENV_DIR).FullName "Scripts") + ";" + $env:PATH
$pythonExecutable = (Join-Path (Get-Item -Path $VENV_DIR).FullName "Scripts" "python.exe")

# Install dependencies
Write-Host "Installing/Upgrading dependencies..."
& pip install -r requirements.txt

# Run the FastAPI application
Write-Host "Starting FastAPI application..."
# The --reload flag is great for development
# For production, remove --reload and consider a process manager like Gunicorn or a Windows Service
& uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload