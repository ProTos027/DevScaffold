$VENV_DIR = "venv"

# Check if virtual environment exists, if not, create it
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Creating virtual environment in $VENV_DIR..."
    python -m venv $VENV_DIR
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
# Check if we're in a PowerShell Core (pwsh) or Windows PowerShell (powershell.exe)
# PS Core uses 'activate.ps1' directly, Windows PowerShell uses 'Activate.ps1'
if ($PSVersionTable.PSEdition -eq 'Core') {
    . "$VENV_DIR/bin/activate.ps1"
} else {
    . "$VENV_DIR/Scripts/Activate.ps1"
}

# Install dependencies
Write-Host "Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Run the FastAPI application
Write-Host "Starting FastAPI application..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
