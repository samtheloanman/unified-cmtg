"""
Production settings for Unified CMTG Platform.

Import base settings and override for production security.
Usage: DJANGO_SETTINGS_MODULE=config.settings_production
"""

from .settings import *  # noqa: F401, F403
import os

# =============================================================================
# SECURITY SETTINGS (Addresses all `manage.py check --deploy` warnings)
# =============================================================================

# Must be False in production
DEBUG = False

# Generate a strong secret key and set via environment variable
# Example: openssl rand -base64 50
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")

# HTTPS Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie Security
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Additional Security Headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# ALLOWED HOSTS (must be explicitly set in production)
# =============================================================================
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split()
if not ALLOWED_HOSTS:
    raise ValueError("DJANGO_ALLOWED_HOSTS environment variable must be set in production")

# =============================================================================
# WAGTAIL SETTINGS
# =============================================================================
WAGTAILADMIN_BASE_URL = os.environ.get('WAGTAILADMIN_BASE_URL', 'https://cms.custommortgageinc.com')

# =============================================================================
# DATABASE (Use production database URL)
# =============================================================================
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True  # Require SSL for production DB connections
    )
}

# =============================================================================
# STATIC FILES (Use WhiteNoise for production static serving)
# =============================================================================
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add WhiteNoise to middleware (after SecurityMiddleware)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# =============================================================================
# LOGGING (Production logging configuration)
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =============================================================================
# CORS (Restrict in production)
# =============================================================================
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split()
CORS_ALLOW_CREDENTIALS = True

# =============================================================================
# EMAIL (Production email backend - configure via environment)
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@custommortgageinc.com')
