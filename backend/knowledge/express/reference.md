# Express.js Framework Reference

## Project Structure
- `app.js` / `server.js` — Entry point
- `routes/` — Route modules
- `controllers/` — Business logic
- `models/` — Database models (Mongoose/Sequelize)
- `middleware/` — Custom middleware
- `config/` — Configuration files

## Version Compatibility
- Express 5.x: Async error handling built-in, `req.query` changes
- Express 4.x: Most widely used, requires `express-async-errors` for async
- Node.js 14+: Required for Express 4.18+
- Node.js 18+: Required for Express 5.x

## Routing
- `app.get('/', handler)`, `app.post('/', handler)`
- `express.Router()` for modular routes
- Path params: `req.params.id`
- Query params: `req.query.search`
- Body: `req.body` (requires `express.json()` middleware)

## Middleware
- `express.json()` — Parse JSON bodies
- `express.urlencoded()` — Parse form data
- `cors` — Cross-origin requests
- `helmet` — Security headers
- Custom: `(req, res, next) => { ... next(); }`

## Database
- MongoDB: `mongoose` for ODM
- PostgreSQL: `sequelize` or `knex`
- Connection: Via `dotenv` + config file

## Authentication
- `jsonwebtoken` for JWT
- `passport` for strategy-based auth
- `bcryptjs` for password hashing

## Error Handling
- Express 4: `app.use((err, req, res, next) => { ... })`
- Express 5: Async errors propagate automatically
- Use `http-errors` for standard error objects

## Startup
- `node app.js` or `nodemon app.js`
- `dotenv.config()` at top of entry file
- `app.listen(PORT, () => console.log(...))`
