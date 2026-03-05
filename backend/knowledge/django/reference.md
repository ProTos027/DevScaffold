# Django Framework Reference

## Directory Layout (REQUIRED — Do not deviate)
```
project_root/
├── manage.py
├── {project_name}/               ← Django project package
│   ├── settings.py
│   ├── urls.py                   ← Root URL conf, includes all app urls
│   ├── wsgi.py
│   └── asgi.py
├── apps/                         ← ALL Django apps live here
│   └── {app_name}/              ← One app per domain (e.g. users, products)
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py             ← ONLY models here (no business logic)
│       ├── serializers.py        ← DRF serializers ONLY
│       ├── views.py              ← ViewSets or APIViews ONLY
│       ├── urls.py               ← App-level URLConf
│       ├── services.py           ← Business logic (called by views, NOT models)
│       └── migrations/
│           └── __init__.py      ← MANDATORY
├── requirements.txt
└── .env
```

## MANDATORY: Custom User Model
**NEVER use the default `django.contrib.auth.models.User` directly.**
1. Create an `accounts` (or `users`) app first.
2. Extend `AbstractUser`:
```python
from django.contrib.auth.models import AbstractUser
class User(AbstractUser):
    # Add custom fields here
    pass
```
3. Register in `settings.py`: `AUTH_USER_MODEL = 'accounts.User'`
*Failure to do this before the first migration will break the project.*

## App Registration (Nested Layout)
Since apps live in `apps/`, their `AppConfig` path is non-standard.
In `settings.py`:
```python
INSTALLED_APPS = [
    ...,
    'apps.accounts.apps.AccountsConfig', 
    'apps.projects.apps.ProjectsConfig',
]
```

### Interface Contract Rules
- Views MUST call `services.py` for logic — NO business logic in views.py.
- Models are data-only — no logic except `__str__` and `Meta`.
- `apps/{app}/urls.py` registers ViewSet routes via `DefaultRouter`.
- All DRF ViewSets inherit from `ModelViewSet` or `GenericViewSet`.
- `settings.py` uses `python-decouple` `config()` for secrets.

## Authentication (DRF + JWT)
Use `djangorestframework-simplejwt`.

**1. Settings Config:**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

**2. Token Endpoints (Root urls.py):**
```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
```

**3. Protecting Views:**
```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@permission_classes([IsAuthenticated])
class ProjectViewSet(ModelViewSet):
    ...
```

## Settings Structure (Examples)
Always use `python-decouple`:
```python
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
DATABASES = {
    'default': config('DATABASE_URL', cast=db_url) # or split fields
}
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS').split(',')
```
