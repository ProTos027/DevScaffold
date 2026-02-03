# Exit immediately if a command exits with a non-zero status.
$ErrorActionPreference = "Stop"

Write-Host "Building the Spring Boot application..."
mvn clean package -DskipTests

if ($LASTEXITCODE -ne 0) {
    Write-Host "Maven build failed. Exiting." -ForegroundColor Red
    exit 1
}

$jarFile = Get-ChildItem -Path "target" -Filter "*.jar" | Where-Object { $_.Name -notmatch "-sources.jar" -and $_.Name -notmatch "-javadoc.jar" } | Select-Object -ExpandProperty FullName

if ([string]::IsNullOrEmpty($jarFile)) {
    Write-Host "No JAR file found in target directory. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "Starting the Spring Boot application: $jarFile"
java -jar $jarFile
