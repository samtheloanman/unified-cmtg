from .base import *
import os
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = ['*']
if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600
        )
    }

CORS_ALLOW_ALL_ORIGINS = True
