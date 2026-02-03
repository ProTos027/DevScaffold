# Ensure Java is installed
if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Host "Java is not installed. Please install Java 17 or higher." -ForegroundColor Red
    exit 1
}

# Ensure Maven is installed
if (-not (Get-Command mvn -ErrorAction SilentlyContinue)) {
    Write-Host "Maven is not installed. Please install Maven 3.6 or higher." -ForegroundColor Red
    exit 1
}

Write-Host "Building the project..."
mvn clean install

if ($LASTEXITCODE -ne 0) {
    Write-Host "Maven build failed. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "Running the Spring Boot application..."
java -jar .\target\url-shortener-0.0.1-SNAPSHOT.jar