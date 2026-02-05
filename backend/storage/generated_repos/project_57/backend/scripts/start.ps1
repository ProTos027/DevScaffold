# --- Virtual Environment Setup ---
$VenvDir = ".venv"
$PythonExec = "python"

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment in $VenvDir/..."
    & $PythonExec -m venv $VenvDir
}

Write-Host "Activating virtual environment..."
# Check if running in a shell that supports direct activation (e.g., cmd.exe in VS Code terminal might not like it)
if ($IsWindows) {
    & "$VenvDir\Scripts\activate.ps1"
} else {
    # For other shells or cases where activate.ps1 might not work directly
    # This part might need adjustment based on specific PowerShell setup
    Write-Host "Please activate the virtual environment manually: .\$VenvDir\Scripts\activate.ps1"
    # Fallback: Directly use python.exe from venv
    $PythonExec = Join-Path $VenvDir "Scripts\python.exe"
    if (-not (Test-Path $PythonExec)) {
        Write-Host "Error: Python executable not found in venv. Please check setup." -ForegroundColor Red
        exit 1
    }
}

# --- Install Dependencies ---
$RequirementsFile = "requirements.txt"
if (Test-Path $RequirementsFile) {
    Write-Host "Installing dependencies from $RequirementsFile..."
    # Ensure pip is run from the activated venv
    if ($IsWindows) {
        & "$VenvDir\Scripts\pip.exe" install --no-cache-dir -r $RequirementsFile
    } else {
        pip install --no-cache-dir -r $RequirementsFile
    }
} else {
    Write-Host "$RequirementsFile not found. Skipping dependency installation."
}

# --- Run FastAPI Application ---
Write-Host "Starting FastAPI application..."
# Ensure uvicorn is run from the activated venv
if ($IsWindows) {
    & "$VenvDir\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Deactivation is not strictly necessary for PowerShell in a script that ends,
# but it's good practice if you intend to continue in the same shell after.
# For a simple run-and-exit script, it's often omitted.
# & "$VenvDir\Scripts\deactivate.ps1"
Write-Host "Application stopped."