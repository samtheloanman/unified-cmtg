from .base import *
import os
import dj_database_url

DEBUG = True
ALLOWED_HOSTS = ['*']
<<<<<<< HEAD

if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600
        )
    }
=======
CORS_ALLOW_ALL_ORIGINS = True
>>>>>>> origin/jules/phase1-foundation-10297780927730413954
