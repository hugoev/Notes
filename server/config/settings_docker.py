"""
Django settings for backend project - Docker configuration.

This module extends the base settings with Docker-specific configurations
for database, CORS, and other environment-specific settings.
"""

import logging
import os

from .constants import ALLOWED_HOSTS, CORS_ALLOWED_ORIGINS
from .settings import *

# Database Configuration for Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'notes_db'),
        'USER': os.environ.get('POSTGRES_USER', 'notes_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'notes_password'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# CORS Configuration for Docker
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS + [
    "http://frontend:3000",  # Docker internal network
]

# Security Configuration
ALLOWED_HOSTS = ALLOWED_HOSTS + ['backend', 'db', 'localhost']

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/tmp/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'notes': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache Configuration (using Redis if available)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email Configuration (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static Files Configuration
STATIC_ROOT = '/app/staticfiles'
MEDIA_ROOT = '/app/media'

# Security Settings for Docker
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database Connection Pooling
DATABASES['default']['CONN_MAX_AGE'] = 60
