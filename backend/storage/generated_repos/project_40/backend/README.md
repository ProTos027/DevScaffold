# URL Shortener API

This is a minimal Spring Boot application that provides a REST API for shortening URLs and redirecting from short codes to original URLs.

## Features
- Shorten a given URL.
- Retrieve the original URL from a short code.
- Redirect to the original URL when accessing a short code.
- In-memory persistence (no external database required).
- Basic error handling.

## Technology Stack
- Spring Boot 3.2.x
- Java 17
- Maven
- Lombok (for boilerplate reduction)

## Getting Started

### Prerequisites
- Java Development Kit (JDK) 17 or higher
- Apache Maven 3.6.x or higher

### Build the Project
Navigate to the root directory of the project (where `pom.xml` is located) and run:

```bash
mvn clean install
```
This will compile the code, run tests, and package the application into a JAR file in the `target/` directory.

### Run the Application

You can run the application using the generated JAR file:

```bash
java -jar target/url-shortener-0.0.1-SNAPSHOT.jar
```

The application will start on `http://localhost:8080` (default port).

#### Using Startup Scripts

**For Linux/macOS:**
Open your terminal, navigate to the project root, and run:
```bash
chmod +x start.sh
./start.sh
```

**For Windows (PowerShell):**
Open PowerShell, navigate to the project root, and run:
```powershell
./start.ps1
```

## API Endpoints
The API runs on `http://localhost:8080`.

### 1. Shorten a URL
- **Endpoint:** `POST /api/shorten`
- **Request Body:**
  ```json
  {
    "url": "https://www.example.com/a-very-long-url-that-needs-shortening"
  }
  ```
- **Response (201 Created):**
  ```json
  {
    "shortUrl": "http://localhost:8080/aBcDeFg",
    "shortCode": "aBcDeFg"
  }
  ```
- **Error (400 Bad Request):** If `url` is missing or empty.

### 2. Get Shortened URL Details
- **Endpoint:** `GET /api/shorten/{shortCode}`
- **Example:** `GET /api/shorten/aBcDeFg`
- **Response (200 OK):**
  ```json
  {
    "shortCode": "aBcDeFg",
    "originalUrl": "https://www.example.com/a-very-long-url-that-needs-shortening",
    "createdAt": "2024-04-23T10:30:00.123456"
  }
  ```
- **Error (404 Not Found):** If the `shortCode` does not exist.

### 3. Redirect to Original URL
- **Endpoint:** `GET /{shortCode}`
- **Example:** `GET /aBcDeFg`
- **Response (301 Moved Permanently):** Redirects to `https://www.example.com/a-very-long-url-that-needs-shortening`.
- **Error (404 Not Found):** If the `shortCode` does not exist.

## Error Handling

The application provides custom error responses for common scenarios:
- `404 Not Found`: When a short code does not exist.
- `400 Bad Request`: When input validation fails (e.g., empty URL).
- `500 Internal Server Error`: For unexpected server-side issues.

Example 404 response:
```json
{
  "timestamp": "2024-04-23T10:30:00.123456",
  "message": "URL not found for short code: nonExistentCode",
  "path": "/nonExistentCode"
}
```
