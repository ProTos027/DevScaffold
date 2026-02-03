# Ensure Maven is installed and Java is set up
if (-not (Get-Command mvn -ErrorAction SilentlyContinue)) {
    Write-Host "Maven is not installed. Please install Maven to proceed."
    exit 1
}

if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Host "Java is not installed. Please install JDK 17 or higher to proceed."
    exit 1
}

Write-Host "Building the Spring Boot application..."
mvn clean install -DskipTests

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed. Exiting."
    exit 1
}

$jarFile = Get-ChildItem -Path "target" -Filter "*.jar" | Select-Object -First 1

if (-not $jarFile) {
    Write-Host "No executable JAR file found in the 'target' directory."
    exit 1
}

Write-Host "Starting the Spring Boot application: $($jarFile.FullName)"
java -jar "$($jarFile.FullName)"
