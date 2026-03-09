"""
Django settings for devscaffold project.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,devscaffold-api.onrender.com').split(',')

# Security settings for Render/Proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=False, cast=bool)


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    
    # Local apps
    'accounts',
    'projects',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'devscaffold.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'devscaffold.wsgi.application'


import dj_database_url

# PostgreSQL configuration (production)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default=f"postgres://{config('DB_USER', default='postgres')}:{config('DB_PASSWORD', default='postgres')}@{config('DB_HOST', default='localhost')}:{config('DB_PORT', default='5432')}/{config('DB_NAME', default='devscaffold')}"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# Custom User Model
AUTH_USER_MODEL = 'accounts.User'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}


# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:5173'
).split(',')

CORS_ALLOW_CREDENTIALS = True


# CSRF Settings for Admin and OAuth
CSRF_TRUSTED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:5173,http://localhost:8000'
).split(',')


# Django Allauth (for GitHub OAuth)
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Email — use console backend in dev (no SMTP server needed)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True  
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # No email verification for OAuth
SOCIALACCOUNT_EMAIL_REQUIRED = False
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'accounts.adapters.AccountAdapter'
LOGIN_REDIRECT_URL = config('FRONTEND_URL', default='http://localhost:5173') + '/dashboard'

# SOCIALACCOUNT_PROVIDERS = {
#     'github': {
#         'APP': {
#             'client_id': config('GITHUB_CLIENT_ID', default=''),
#             'secret': config('GITHUB_CLIENT_SECRET', default=''),
#         },
#         'SCOPE': [
#             'user',
#             'repo',
#         ],
#     }
# }

# Increase timeout for OAuth API requests to prevent connection errors
SOCIALACCOUNT_REQUESTS_TIMEOUT = 30  # seconds


# File Storage Settings
STORAGE_PATH = BASE_DIR / config('STORAGE_PATH', default='storage/generated_repos')
STORAGE_PATH.mkdir(parents=True, exist_ok=True)

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default=None)
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default=None)
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    # Use S3 for project uploads
    PROJECT_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    PROJECT_STORAGE = 'django.core.files.storage.FileSystemStorage'
    MEDIA_ROOT = STORAGE_PATH

REPO_RETENTION_HOURS = config('REPO_RETENTION_HOURS', default=24, cast=int)


# Encryption for API Keys
_raw_key = config('ENCRYPTION_KEY', default='').strip("'\" ")
ENCRYPTION_KEY = _raw_key.encode() if _raw_key else None

# Boot-time validation to catch config errors early in logs
if ENCRYPTION_KEY:
    try:
        from cryptography.fernet import Fernet
        Fernet(ENCRYPTION_KEY)
    except Exception as e:
        import logging
        # We log the length to help diagnose padding/copy-paste issues without leaking the key
        logging.error(f"STATIC_CHECK: ENCRYPTION_KEY is INVALID. Length: {len(_raw_key)}. Error: {str(e)}")


# Site Configuration
SITE_DOMAIN = config('SITE_DOMAIN', default='localhost:8000')
SITE_NAME = config('SITE_NAME', default='DevScaffold')
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')
