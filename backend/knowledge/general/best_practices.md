# General Best Practices

## Environment Variables
- Never hardcode secrets (API keys, DB passwords, SECRET_KEY)
- Use `.env` file for development, environment variables for production
- Python: `python-decouple` or `django-environ`
- Node.js: `dotenv`
- Java: `application.properties` with `${ENV_VAR}` syntax

## .gitignore Essentials
- `node_modules/`, `__pycache__/`, `.env`, `*.pyc`
- `venv/`, `.venv/`, `env/`
- IDE: `.idea/`, `.vscode/`, `*.swp`
- Build artifacts: `dist/`, `build/`, `target/`
- `*.sqlite3`, `*.db` (development databases)

## CORS Configuration
- Always configure CORS for frontend-backend communication
- Restrict origins in production (no `*` wildcard)
- Allow credentials if using cookies/JWT in headers

## Authentication Patterns
- JWT: Stateless, `Authorization: Bearer <token>`
- Session: Server-side, cookie-based
- OAuth2: For social login (Google, GitHub)
- Always hash passwords (bcrypt, argon2)

## API Design
- RESTful: Use HTTP methods correctly (GET read, POST create, PUT update, DELETE remove)
- Consistent error responses: `{"detail": "Error message"}`
- Pagination for list endpoints
- Version your API: `/api/v1/`

## Database
- Use migrations for schema changes
- Add indexes for frequently queried fields
- Use transactions for multi-table operations
- Never store passwords in plain text

## Project README
- Include: Description, setup instructions, environment variables
- include: How to run development server
- Include: API documentation or link to Swagger/OpenAPI
