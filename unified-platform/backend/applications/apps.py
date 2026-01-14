"""
Applications App Configuration
"""

from django.apps import AppConfig


class ApplicationsConfig(AppConfig):
    """Configuration for the Applications app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications'
    verbose_name = 'Loan Applications'
