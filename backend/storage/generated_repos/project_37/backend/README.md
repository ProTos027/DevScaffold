# URL Shortener Spring Boot Application

This is a minimal Spring Boot application for shortening URLs, built with Maven, Spring Data JPA, and PostgreSQL.

## Features

-   Shorten long URLs to unique short codes.
-   Redirect short codes to original long URLs.
-   Track click counts for shortened URLs.
-   Database schema management with Flyway.
-   Basic error handling.

## Technologies Used

-   **Spring Boot**: Web, Data JPA
-   **Maven**: Build automation
-   **PostgreSQL**: Relational database
-   **Flyway**: Database migration tool
-   **Java 17**

## Prerequisites

Before you begin, ensure you have met the following requirements:

*   Java Development Kit (JDK) 17 or higher installed.
*   Maven installed.
*   PostgreSQL installed and running.

## Setup and Run

### 1. Database Setup

Create a PostgreSQL database named `urlshortener_db` (or whatever you configure in `application.properties`) and a user if needed.

```sql
CREATE DATABASE urlshortener_db;
CREATE USER postgres WITH PASSWORD 'password'; -- If not already exists, or use your existing user
GRANT ALL PRIVILEGES ON DATABASE urlshortener_db TO postgres;
```

Make sure the `spring.datasource.username` and `spring.datasource.password` in `src/main/resources/application.properties` match your PostgreSQL credentials.

### 2. Build the Application

Navigate to the project root directory and build the application using Maven:

```bash
mvn clean install
```

### 3. Run the Application

#### On Linux/macOS

```bash
./start.sh
```

#### On Windows (PowerShell)

```powershell
./start.ps1
```

Alternatively, you can run the JAR file directly:

```bash
java -jar target/urlshortener-0.0.1-SNAPSHOT.jar
```

### 4. API Endpoints

The application will be running on `http://localhost:8080` (or the port configured in `application.properties`).

#### Shorten a URL

-   **Method**: `POST`
-   **Endpoint**: `/shorten`
-   **Content-Type**: `application/json`
-   **Request Body Example**:
    ```json
    {
        "longUrl": "https://www.example.com/very/long/url/that/needs/to/be/shortened"
    }
    ```
-   **Response Example**:
    ```json
    {
        "shortUrl": "http://localhost:8080/abcd12"
    }
    ```

#### Redirect to Original URL

-   **Method**: `GET`
-   **Endpoint**: `/{shortCode}`
-   **Example**: `http://localhost:8080/abcd12` will redirect to the original long URL.

## Development

### Database Migrations

This project uses Flyway for database schema management. Migration scripts are located in `src/main/resources/db/migration/`. When the application starts, Flyway automatically applies any pending migrations. To add a new migration:

1.  Create a new SQL file in `src/main/resources/db/migration/` following the naming convention `V<VERSION>__<DESCRIPTION>.sql` (e.g., `V2__Add_new_column.sql`).
2.  Write your SQL schema changes in this file.
3.  Run the application, and Flyway will apply the new migration.

### Error Handling

Global error handling is implemented via `GlobalExceptionHandler` to provide consistent error responses.

-   `404 Not Found`: For invalid short codes.
-   `400 Bad Request`: For invalid request bodies (e.g., empty or malformed URLs).
-   `500 Internal Server Error`: For unexpected server-side issues.
