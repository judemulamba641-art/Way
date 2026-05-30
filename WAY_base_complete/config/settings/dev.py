from .base import *

DEBUG = True

APP_ENV = "development"

ALLOWED_HOSTS = ["*"]


# ---------------------------------------------------------
# DATABASE DEV
# ---------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ---------------------------------------------------------
# LOGGING DEV
# ---------------------------------------------------------
LOG_LEVEL = "DEBUG"