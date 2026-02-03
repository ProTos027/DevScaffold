# Exit immediately if a command exits with a non-zero status.
$ErrorActionPreference = "Stop"

$VENV_PATH = ".venv"
$REQUIREMENTS_FILE = "requirements.txt"

Write-Host "Starting FastAPI project..."

# Check if virtual environment exists, create if not
if (-not (Test-Path $VENV_PATH -PathType Container)) {
    Write-Host "Creating virtual environment at $VENV_PATH..."
    python -m venv $VENV_PATH
    Write-Host "Virtual environment created."
} else {
    Write-Host "Virtual environment already exists."
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
# On Windows, the activate script is in Scripts/
if (Test-Path "$VENV_PATH\Scripts\Activate.ps1") {
    & "$VENV_PATH\Scripts\Activate.ps1"
} elseif (Test-Path "$VENV_PATH\Scripts\activate") { # Fallback for other shell types
    & "$VENV_PATH\Scripts\activate"
} else {
    Write-Warning "Could not find virtual environment activation script. Please activate manually."
}
Write-Host "Virtual environment activated."

# Install dependencies
if (Test-Path $REQUIREMENTS_FILE) {
    Write-Host "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --no-cache-dir -r $REQUIREMENTS_FILE
    Write-Host "Dependencies installed."
} else {
    Write-Warning "Warning: $REQUIREMENTS_FILE not found. Skipping dependency installation."
}

# Run FastAPI application
Write-Host "Starting Uvicorn server..."
# --reload for development, remove for production
uvicorn main:app --reload --host 0.0.0.0 --port 8000
