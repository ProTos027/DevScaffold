# URL Shortener Spring Boot Application

This is a minimal URL shortener application built with Spring Boot.

## Features
- Generate short codes for long URLs.
- Redirect from short codes to original URLs.
- Basic click counting for short URLs.
- In-memory storage (no external database required).

## Getting Started

### Prerequisites
- Java 17 or higher
- Maven 3.6 or higher

### Build and Run

#### Linux / macOS
1. Open a terminal in the project root directory.
2. Make the `start.sh` script executable:
   `chmod +x start.sh`
3. Run the application:
   `./start.sh`

#### Windows
1. Open PowerShell in the project root directory.
2. Run the application:
   `.\start.ps1`

This will compile the project, package it into a JAR file, and then run the application. The application will be accessible on `http://localhost:8080`.

## API Endpoints

### 1. Create a Short URL
- **URL**: `/api/shorten`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Request Body Example**:
  ```json
  {
    "originalUrl": "https://www.example.com/very/long/url/that/needs/to/be/shortened"
  }
  ```
- **Response Body Example**:
  ```json
  {
    "originalUrl": "https://www.example.com/very/long/url/that/needs/to/be/shortened",
    "shortUrl": "http://localhost:8080/abcde"
  }
  ```

### 2. Redirect Short URL
- **URL**: `/{shortCode}` (e.g., `/abcde`)
- **Method**: `GET`
- Redirects to the `originalUrl` associated with the `shortCode`.

## Project Structure

- `src/main/java/com/example/urlshortener`:
    - `UrlShortenerApplication.java`: Main entry point.
    - `controller`: REST API endpoints.
    - `exception`: Custom exception and global exception handler.
    - `model`: Data model for URLs.
    - `repository`: In-memory data storage (simulating a database).
    - `service`: Business logic for URL shortening.
- `src/main/resources/application.properties`: Application configuration.
- `pom.xml`: Maven project file.
- `start.sh`: Startup script for Linux/macOS.
- `start.ps1`: Startup script for Windows.
