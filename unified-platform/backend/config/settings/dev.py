"""
Development settings for Unified CMTG Platform.
"""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Relax CORS for development
CORS_ALLOW_ALL_ORIGINS = True

# Use console backend for emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Optional: Disable password validators for easier testing
AUTH_PASSWORD_VALIDATORS = []
