# Django Framework Reference

## Project Structure
- `manage.py` — CLI entry point
- `settings.py` — All config (INSTALLED_APPS, MIDDLEWARE, DATABASES)
- `urls.py` — URL routing with `path()` (Django 2.0+)
- `wsgi.py` / `asgi.py` — Deployment entry points

## Version Compatibility
- Django 5.x: Python 3.10+, `path()` routing, async views native
- Django 4.2 LTS: Python 3.8+, last version supporting Python 3.8/3.9
- Django 3.x: `url()` deprecated, use `path()` and `re_path()`

## Models
- All models inherit `models.Model`
- Use `models.CharField`, `models.TextField`, `models.IntegerField`, etc.
- ForeignKey requires `on_delete` (CASCADE, SET_NULL, PROTECT)
- Django 5.x: `GeneratedField` for computed columns
- Always add `__str__` method for admin display
- Use `Meta` class for ordering, verbose names, constraints

## REST Framework (DRF)
- Serializers: `ModelSerializer` for CRUD, `Serializer` for custom
- ViewSets: `ModelViewSet` for full CRUD, `@action` for custom endpoints
- Router: `DefaultRouter` auto-generates URL patterns
- Permissions: `IsAuthenticated`, `IsAdminUser`, custom permission classes
- Pagination: Set in `REST_FRAMEWORK` settings

## Authentication
- `django-allauth` for social auth
- `djangorestframework-simplejwt` for JWT
- Token in Authorization header: `Bearer <token>`

## Database
- Default: SQLite (development)
- Production: PostgreSQL via `psycopg2-binary`
- Migrations: `makemigrations` then `migrate`
- Never edit migration files manually

## Settings Best Practices
- Use `python-decouple` or `django-environ` for env vars
- `SECRET_KEY`: Always from environment, never hardcoded
- `DEBUG = False` in production
- `ALLOWED_HOSTS`: Must be set in production
- `CORS_ALLOWED_ORIGINS`: Use `django-cors-headers`
