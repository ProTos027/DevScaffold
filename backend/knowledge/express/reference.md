# Express.js Framework Reference

## Directory Layout (REQUIRED — Do not deviate)
```
backend/
├── server.js                   ← Entry: dotenv, app setup, listen
├── app.js                      ← Express app, CORS, middleware, router registration
├── routes/                     ← ONE file per resource (e.g. userRoutes.js)
│   └── {resource}Routes.js     ← express.Router(), delegates to controllers
├── controllers/                ← Request/response handling (calls services)
│   └── {resource}Controller.js
├── services/                   ← Business logic (no req/res awareness)
│   └── {resource}Service.js
├── models/                     ← DB schema definitions (Mongoose/Sequelize)
│   └── {Entity}.js
├── middleware/                 ← Auth, error handling, logging
│   ├── authMiddleware.js
│   └── errorHandler.js
├── config/
│   └── db.js                   ← Database connection
├── package.json
└── .env
```

### Interface Contract Rules
- Controllers only handle req/res — all logic MUST delegate to a Service.
- Service methods: `async methodName(params) { ... }` — NO req/res access.
- Routes import controllers, NOT services directly.
- Error handler middleware is the LAST `app.use()` in app.js.

## Project Structure
- `app.js` / `server.js` — Entry point
- `routes/` — Route modules
- `controllers/` — Business logic
- `models/` — Database models (Mongoose/Sequelize)
- `middleware/` — Custom middleware
- `config/` — Configuration files

## Version Compatibility
- Express 5.x: Async error handling built-in, `req.query` changes
- Express 4.x: Most widely used, **MANDATORY**: `require('express-async-errors')` at top of `app.js` for async handlers.
- Node.js 14+: Required for Express 4.18+
- Node.js 18+: Required for Express 5.x

## app.js Canonical Structure (REQUIRED ORDER)
```js
require('dotenv').config();
require('express-async-errors'); // MUST be before routes (Express 4)
const express = require('express');
const cors = require('cors');
const app = express();

// 1. Global Middleware
app.use(cors());
app.use(express.json());

// 2. Routes
app.use('/api/users', require('./routes/userRoutes'));

// 3. Error Handler (MUST BE LAST)
app.use(require('./middleware/errorHandler'));
```

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
- PostgreSQL: `pg` (node-postgres) for raw queries OR `sequelize`/`knex` for ORM

### Pool Import — CORRECT PATTERN (Critical)
```js
// config/db.js — create pool ONCE, export it
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
module.exports = { pool };

// models/gameModel.js — import with EXACT destructuring
const { pool } = require('../config/db');  // ← correct relative path from models/
const { pool } = require('../../config/db'); // ← if model is in subdirectory
```
- NEVER `const pool = require('../config/db')` — pool is a named export, must destructure
- NEVER recreate `new Pool()` outside of `config/db.js`

## Authentication
- `jsonwebtoken` for JWT
- `bcryptjs` for password hashing

### Auth Middleware — CRITICAL: Always return after responding
```js
// middleware/authMiddleware.js
const authenticate = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' }); // ← MUST return
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid token' }); // ← MUST return
  }
};
```
- ALWAYS `return res.json(...)` in middleware — missing `return` causes double-respond crash

### Ownership Check — ALWAYS validate in Controller
```js
// controllers/gameController.js
const updateGame = async (req, res) => {
  const game = await gameService.findById(req.params.id);
  
  // Rule: Logic involving req/res (like auth checks) stays in Controller
  if (game.player_id !== req.user.id) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  
  const updated = await gameService.update(req.params.id, req.body);
  res.json(updated);
};
```

### WebSocket Authentication
```js
wss.on('connection', (ws, req) => {
  const token = new URLSearchParams(req.url.split('?')[1]).get('token');
  try {
    const user = jwt.verify(token, process.env.JWT_SECRET);
    ws.user = user;
  } catch {
    ws.close(1008, 'Unauthorized');
    return;
  }
});
```

## Error Handling
- Express 4: `app.use((err, req, res, next) => { ... })`
- Express 5: Async errors propagate automatically
- Use `http-errors` for standard error objects

## Startup
- `node app.js` or `nodemon app.js`
- `dotenv.config()` at top of entry file
- `app.listen(PORT, () => console.log(...))`
