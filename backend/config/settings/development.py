"""
Development settings for Job Scraper project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# Use PostgreSQL if DATABASE_URL is set (Docker environment), otherwise SQLite for local development
if env('DATABASE_URL', default=None):
    DATABASES = {
        'default': env.db()
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Add development-specific apps
INSTALLED_APPS += [
    'django_extensions',
]

# Development-specific middleware
# Debug toolbar removed for now

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Disable SSL redirect in development
SECURE_SSL_REDIRECT = False
