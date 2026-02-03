# Exit immediately if a command exits with a non-zero status.
$ErrorActionPreference = "Stop"

$VENV_DIR = ".venv"

Write-Host "Checking for virtual environment..."
if (-not (Test-Path $VENV_DIR -PathType Container)) {
    Write-Host "Creating virtual environment '$VENV_DIR'...";
    python -m venv $VENV_DIR;
}

Write-Host "Activating virtual environment..."
# On Windows, activate.ps1 is in Scripts
if (Test-Path "$VENV_DIR/Scripts/Activate.ps1") {
    & "$VENV_DIR/Scripts/Activate.ps1";
} elseif (Test-Path "$VENV_DIR/bin/activate") {
    # For Git Bash or WSL, it might be in bin
    & "$VENV_DIR/bin/activate";
} else {
    Write-Error "Could not find virtual environment activation script.";
    exit 1;
}


Write-Host "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Starting FastAPI application..."
# Run with reload for development
uvicorn main:app --reload --host 0.0.0.0 --port 8000
